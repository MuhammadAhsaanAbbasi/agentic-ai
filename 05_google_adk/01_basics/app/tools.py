import datetime
from zoneinfo import ZoneInfo
from typing import Dict, Union
import requests as rq
from pydantic import ValidationError

from adktools import adk_tool
from app.models import GetCurrentTimeInput, TimeResult, InvalidTimezoneError

@adk_tool(
    name="get_weather",
    description="Get the Weather of the location through longitude & latitude",
)
def get_weather(longitude: float, latitude: float):
    """
    Get the Weather of the location through longitude & latitude

    Args:
        longitude (float): The longitude of the location
        latitude (float): The latitude of the location

    Returns:
        str: The weather data of that latitude & longitude city.
    """
    BASE_URL = f"https://api.open-meteo.com/v1/forecast"
    params: Dict[str, Union[str, int, float]] = {
        "latitude" : latitude,
        "longitude" : longitude,
        "hourly" : "temperature_2m",
        "forecast_days" : 1
    }

    response = rq.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
    else:
        raise Exception(f"API Request Failed: {response.status_code}, {response.text}")

    current_time = datetime.datetime.utcnow()
    time_list = [datetime.datetime.fromisoformat(t.replace("Z", "+00:00")) for t in data["hourly"]["time"]]
    temperature_lists = data["hourly"]["temperature_2m"]

    closet_time_index = min(range(len(time_list)), key=lambda i: abs(time_list[i] - current_time))

    temperature = temperature_lists[closet_time_index]

    return f"The Current temperature at {latitude}, {longitude} is {temperature}°C"

@adk_tool
def get_timezones_list() -> dict:
    """Returns a list of common IANA timezones grouped by region."""
    timezones = {
        "North America": ["America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles"],
        "Europe": ["Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Rome"],
        "Asia": ["Asia/Tokyo", "Asia/Singapore", "Asia/Dubai", "Asia/Shanghai"],
        "Australia": ["Australia/Sydney", "Australia/Melbourne", "Australia/Perth"]
    }
    return timezones

@adk_tool(
    name="get_time",
    description="Get the current time in a specified timezone. Accepts IANA timezone identifiers."
)
def get_current_time(timezone: str) -> TimeResult | InvalidTimezoneError:
    """Get current time in a specified timezone
    
    Args:
        timezone (str): The timezone for which to retrieve the current time.

    Returns:
        TimeResult: The current time information for the specified timezone.
        InvalidTimezoneError: If the timezone is invalid or cannot be found.
    """
    # Primary validation with domain-specific error handling
    try:
        # Validate the input
        validated_input = GetCurrentTimeInput(timezone=timezone)
    except ValidationError:
        # Return domain-specific error for input validation failures
        return InvalidTimezoneError(
            timezone=timezone,
            message=f"Invalid timezone format: '{timezone}'"
        )
    
    # Timezone resolution with domain-specific error handling
    try:
        # Get the timezone
        tz = ZoneInfo(validated_input.timezone)
    except Exception:
        # Return domain-specific error for timezone not found
        return InvalidTimezoneError(
            timezone=validated_input.timezone,
            message=f"Unknown timezone: '{validated_input.timezone}'"
        )
    
    # Business logic - get current time
    try:
        now = datetime.datetime.now(tz)
        
        # Return the successful result
        return TimeResult(
            timezone=validated_input.timezone,
            datetime=now.isoformat(timespec="seconds"),
            is_dst=bool(now.dst())
        )
    except Exception as e:
        # Let the decorator catch any unexpected errors
        raise RuntimeError(f"Error getting time data: {str(e)}")