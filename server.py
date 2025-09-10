import json
import logging
from typing import Any, Optional

import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
OPENMETEO_API_BASE = "https://api.open-meteo.com/v1"
GEOCODING_API_BASE = "https://geocoding-api.open-meteo.com/v1"
USER_AGENT = "weather-app/1.0"

# Initialize FastMCP server
mcp = FastMCP("weather")


async def make_openmeteo_request(url: str) -> Optional[dict[str, Any]]:
    """Make a request to the Open-Meteo API with proper error handling.

    Args:
        url: The complete URL to make the request to

    Returns:
        JSON response data as a dictionary, or None if request fails
    """
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Making request to: {url}")
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return await response.json()
    except httpx.TimeoutException:
        logger.error(f"Timeout error for URL: {url}")
        return None
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code} for URL: {url}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error for URL {url}: {e}")
        return None


@mcp.tool()
async def get_current_weather(latitude: float, longitude: float) -> str:
    """Get current weather for a location.

    Args:
        latitude: Latitude of the location (-90 to 90)
        longitude: Longitude of the location (-180 to 180)

    Returns:
        JSON string containing current weather data
    """
    # Validate coordinates
    if not (-90 <= latitude <= 90):
        return json.dumps({"error": "Latitude must be between -90 and 90"})
    if not (-180 <= longitude <= 180):
        return json.dumps({"error": "Longitude must be between -180 and 180"})
    try:
        params = (
            "temperature_2m,is_day,showers,cloud_cover,wind_speed_10m,"
            "wind_direction_10m,pressure_msl,snowfall,precipitation,"
            "relative_humidity_2m,apparent_temperature,rain,weather_code,"
            "surface_pressure,wind_gusts_10m"
        )
        url = (
            f"{OPENMETEO_API_BASE}/forecast?"
            f"latitude={latitude}&longitude={longitude}&current={params}"
        )

        data = await make_openmeteo_request(url)

        if not data:
            return json.dumps({
                "error": (
                    "Unable to fetch current weather data for this location."
                )
            })

        return json.dumps(data, indent=2)
    except Exception as e:
        logger.error(f"Error in get_current_weather: {e}")
        return json.dumps({
            "error": f"Error fetching weather data: {str(e)}"
        })


@mcp.tool()
async def get_forecast(
    latitude: float, longitude: float, days: int = 7
) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location (-90 to 90)
        longitude: Longitude of the location (-180 to 180)
        days: Number of forecast days (1-16, default 7)

    Returns:
        JSON string containing forecast data
    """
    # Validate coordinates
    if not (-90 <= latitude <= 90):
        return json.dumps({"error": "Latitude must be between -90 and 90"})
    if not (-180 <= longitude <= 180):
        return json.dumps({"error": "Longitude must be between -180 and 180"})
    try:
        forecast_days = min(max(days, 1), 16)  # Clamp between 1-16
        params = (
            "temperature_2m_max,temperature_2m_min,precipitation_sum,"
            "wind_speed_10m_max,weather_code"
        )
        url = (
            f"{OPENMETEO_API_BASE}/forecast?"
            f"latitude={latitude}&longitude={longitude}&daily={params}"
            f"&forecast_days={forecast_days}"
        )

        data = await make_openmeteo_request(url)

        if not data:
            return json.dumps(
                {"error": "Unable to fetch forecast data for this location."}
            )

        return json.dumps(data, indent=2)
    except Exception as e:
        logger.error(f"Error in get_forecast: {e}")
        return json.dumps({"error": f"Error fetching forecast data: {str(e)}"})


@mcp.tool()
async def get_location(name: str) -> str:
    """Search for locations by name to get coordinates.

    Args:
        name: Name of the city or location to search for

    Returns:
        JSON string containing location search results
    """
    try:
        if not name.strip():
            return json.dumps({"error": "Location name cannot be empty."})

        url = (
            f"{GEOCODING_API_BASE}/search?"
            f"name={name}&count=5&language=en&format=json"
        )

        data = await make_openmeteo_request(url)

        if not data:
            return json.dumps({"error": "Unable to search for locations."})

        return json.dumps(data, indent=2)
    except Exception as e:
        logger.error(f"Error in get_location: {e}")
        return json.dumps({"error": f"Error searching for location: {str(e)}"})


if __name__ == "__main__":
    mcp.run(transport="stdio")
