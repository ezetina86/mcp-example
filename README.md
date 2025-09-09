# MCP Weather Server

A Model Context Protocol (MCP) server that provides weather data through the Open-Meteo API. Built with FastMCP and Python, offering real-time weather information, forecasts, and location search capabilities.

## Features

- **Current Weather**: Real-time weather conditions including temperature, humidity, wind, and precipitation
- **Weather Forecast**: Multi-day forecasts (1-16 days) with daily temperature ranges and conditions
- **Location Search**: Geocoding service to find coordinates for cities and locations worldwide
- **No API Key Required**: Uses the free Open-Meteo API
- **Comprehensive Error Handling**: Robust logging and exception management
- **PEP8 Compliant**: Clean, maintainable Python code

## Available Tools

### get_current_weather(latitude, longitude)
Retrieves current weather conditions for specified coordinates including:
- Temperature, apparent temperature, humidity
- Wind speed, direction, and gusts
- Precipitation, rain, snowfall
- Atmospheric pressure and cloud cover
- Weather codes and day/night status

### get_forecast(latitude, longitude, days=7)
Provides weather forecast for 1-16 days with:
- Daily temperature maximums and minimums
- Precipitation totals
- Maximum wind speeds
- Weather condition codes

### get_location(name)
Searches for locations by name and returns:
- Geographical coordinates (latitude/longitude)
- Location details and administrative information
- Multiple matching results for disambiguation

## Technical Details

- **Language**: Python 3.8+
- **Framework**: FastMCP
- **HTTP Client**: httpx with async support
- **APIs**: Open-Meteo Weather & Geocoding APIs
- **Transport**: stdio (standard input/output)
- **Logging**: Structured logging with error tracking

## Installation & Setup

### 1. Install Dependencies

**Using uv (recommended):**
```bash
cd mcp-example
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

**Using standard venv:**
```bash
cd mcp-example
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Tests
```bash
pytest test_server.py -v
```

### 3. Test the Server
```bash
python server.py
```

### 4. Configure MCP Client

Add to your MCP client configuration:

**Option 1: Using Python directly (recommended)**
```json
{
  "weather": {
    "command": "python",
    "args": ["/path/to/mcp-example/server.py"],
    "env": {},
    "working_directory": "/path/to/mcp-example"
  }
}
```

**Option 2: Using uv (if installed)**
```json
{
  "weather": {
    "command": "/opt/homebrew/bin/uv",
    "args": [
      "run",
      "--with",
      "mcp[cli]",
      "mcp",
      "run",
      "/path/to/mcp-example/server.py"
    ],
    "env": {},
    "working_directory": null
  }
}
```

## Usage Examples

Once configured, you can interact with the weather server through your MCP client:

- "What's the current weather in Tokyo?"
- "Get a 5-day forecast for New York"
- "Find the coordinates for London, UK"
- "What's the weather like at latitude 40.7128, longitude -74.0060?"

## Dependencies

- `httpx`: Async HTTP client for API requests
- `mcp`: Model Context Protocol framework
- `pytest`: Testing framework
- `pytest-asyncio`: Async test support

## Project Structure

```
mcp-example/
├── server.py          # Main MCP server implementation
├── test_server.py     # Test suite
├── requirements.txt   # Python dependencies
└── README.md         # This documentation
```

## Testing

Run the test suite to verify functionality:

```bash
# Activate virtual environment first
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pytest test_server.py -v
```

The test suite covers:
- API request handling and error cases
- All weather tool functions
- Input validation and parameter clamping
- Network timeout and HTTP error scenarios

### Test Plan

| Test Case | Description | Expected Result |
|-----------|-------------|----------------|
| `test_make_openmeteo_request_timeout` | API request timeout | Returns `None` |
| `test_get_current_weather_success` | Valid coordinates | Returns JSON weather data |
| `test_get_current_weather_failure` | API failure | Returns error message |
| `test_get_forecast_success` | Valid forecast request | Returns JSON forecast data |
| `test_get_forecast_days_clamping` | Days parameter > 16 | Clamps to 16 days max |
| `test_get_location_success` | Valid location name | Returns JSON location data |
| `test_get_location_empty_name` | Empty location string | Returns validation error |
| `test_get_location_failure` | API failure | Returns error message |

## Error Handling

The server includes comprehensive error handling:
- Network timeouts and connection errors
- HTTP status code validation
- Input parameter validation (empty names, parameter clamping)
- Structured logging for debugging
- Graceful fallbacks for API failures

## Test Coverage

- **API Integration**: Timeout and error handling
- **Input Validation**: Empty strings, parameter bounds
- **Function Logic**: All three weather tools
- **Error Scenarios**: Network failures, invalid responses
- **Parameter Handling**: Days clamping (1-16), coordinate validation