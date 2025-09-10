import json
import pytest
from unittest.mock import patch
import httpx

from server import (
    make_openmeteo_request,
    get_current_weather,
    get_forecast,
    get_location,
)


@pytest.mark.asyncio
async def test_make_openmeteo_request_timeout():
    """Test API request timeout."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.side_effect = (
            httpx.TimeoutException("Timeout")
        )

        result = await make_openmeteo_request("http://test.com")
        assert result is None


@pytest.mark.asyncio
async def test_get_current_weather_success():
    """Test successful current weather request."""
    mock_data = {"current": {"temperature_2m": 20.5}}

    with patch("server.make_openmeteo_request", return_value=mock_data):
        result = await get_current_weather(40.7128, -74.0060)
        assert json.loads(result) == mock_data


@pytest.mark.asyncio
async def test_get_current_weather_failure():
    """Test failed current weather request."""
    with patch("server.make_openmeteo_request", return_value=None):
        result = await get_current_weather(40.7128, -74.0060)
        data = json.loads(result)
        assert "error" in data
        assert "Unable to fetch current weather data" in data["error"]


@pytest.mark.asyncio
async def test_get_forecast_success():
    """Test successful forecast request."""
    mock_data = {"daily": {"temperature_2m_max": [25.0, 26.0]}}

    with patch("server.make_openmeteo_request", return_value=mock_data):
        result = await get_forecast(40.7128, -74.0060, 5)
        assert json.loads(result) == mock_data


@pytest.mark.asyncio
async def test_get_forecast_days_clamping():
    """Test forecast days parameter clamping."""
    mock_data = {"daily": {"temperature_2m_max": [25.0]}}

    with patch(
        "server.make_openmeteo_request", return_value=mock_data
    ) as mock_request:
        await get_forecast(40.7128, -74.0060, 20)  # Should clamp to 16

        # Check that the URL contains forecast_days=16
        call_args = mock_request.call_args[0][0]
        assert "forecast_days=16" in call_args


@pytest.mark.asyncio
async def test_get_location_success():
    """Test successful location search."""
    mock_data = {"results": [{"name": "New York", "latitude": 40.7128}]}

    with patch("server.make_openmeteo_request", return_value=mock_data):
        result = await get_location("New York")
        assert json.loads(result) == mock_data


@pytest.mark.asyncio
async def test_get_location_empty_name():
    """Test location search with empty name."""
    result = await get_location("")
    data = json.loads(result)
    assert "error" in data
    assert "Location name cannot be empty" in data["error"]


@pytest.mark.asyncio
async def test_get_location_failure():
    """Test failed location search."""
    with patch("server.make_openmeteo_request", return_value=None):
        result = await get_location("NonexistentCity")
        data = json.loads(result)
        assert "error" in data
        assert "Unable to search for locations" in data["error"]


@pytest.mark.asyncio
async def test_get_current_weather_invalid_latitude():
    """Test current weather with invalid latitude."""
    result = await get_current_weather(91.0, -74.0060)
    data = json.loads(result)
    assert "error" in data
    assert "Latitude must be between -90 and 90" in data["error"]


@pytest.mark.asyncio
async def test_get_current_weather_invalid_longitude():
    """Test current weather with invalid longitude."""
    result = await get_current_weather(40.7128, 181.0)
    data = json.loads(result)
    assert "error" in data
    assert "Longitude must be between -180 and 180" in data["error"]


@pytest.mark.asyncio
async def test_get_forecast_invalid_coordinates():
    """Test forecast with invalid coordinates."""
    result = await get_forecast(-91.0, 200.0)
    data = json.loads(result)
    assert "error" in data
    assert "Latitude must be between -90 and 90" in data["error"]


@pytest.mark.asyncio
async def test_make_openmeteo_request_http_error():
    """Test API request HTTP error."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = httpx.Response(404)
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        mock_response.raise_for_status = lambda: (_ for _ in ()).throw(
            httpx.HTTPStatusError("Not found", request=None, response=mock_response)
        )

        result = await make_openmeteo_request("http://test.com")
        assert result is None


@pytest.mark.asyncio
async def test_make_openmeteo_request_json_error():
    """Test API request JSON parsing error."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = httpx.Response(200)
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        mock_response.raise_for_status = lambda: None
        mock_response.json = lambda: (_ for _ in ()).throw(ValueError("Invalid JSON"))

        result = await make_openmeteo_request("http://test.com")
        assert result is None


@pytest.mark.asyncio
async def test_get_current_weather_exception():
    """Test current weather with unexpected exception."""
    with patch("server.make_openmeteo_request", side_effect=ValueError("Test error")):
        result = await get_current_weather(40.7128, -74.0060)
        data = json.loads(result)
        assert "error" in data
        assert "Error fetching weather data" in data["error"]


@pytest.mark.asyncio
async def test_get_forecast_exception():
    """Test forecast with unexpected exception."""
    with patch("server.make_openmeteo_request", side_effect=RuntimeError("Test error")):
        result = await get_forecast(40.7128, -74.0060)
        data = json.loads(result)
        assert "error" in data
        assert "Error fetching forecast data" in data["error"]


@pytest.mark.asyncio
async def test_get_location_exception():
    """Test location search with unexpected exception."""
    with patch("server.make_openmeteo_request", side_effect=ConnectionError("Test error")):
        result = await get_location("Test City")
        data = json.loads(result)
        assert "error" in data
        assert "Error searching for location" in data["error"]
