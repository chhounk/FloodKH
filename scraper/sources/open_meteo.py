"""
FloodKH -- Open-Meteo API client.

Fetches weather forecast/historical data and river-discharge estimates from
the free Open-Meteo APIs.  No API key required.

Endpoints used:
    https://api.open-meteo.com/v1/forecast   (weather)
    https://flood-api.open-meteo.com/v1/flood (river discharge)
"""

import requests

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
FLOOD_URL = "https://flood-api.open-meteo.com/v1/flood"

# Timeout for every HTTP request (seconds).
REQUEST_TIMEOUT = 15


def fetch_weather_data(lat: float, lon: float) -> dict | None:
    """Fetch rainfall and soil-moisture data for a coordinate.

    Queries Open-Meteo for 7 past days + 3-day forecast of daily
    precipitation and surface soil moisture.

    Returns
    -------
    dict with keys:
        rainfall_24h   : float  -- precipitation in last 24 h (mm)
        rainfall_3d    : float  -- cumulative precipitation, last 3 days (mm)
        rainfall_7d    : float  -- cumulative precipitation, last 7 days (mm)
        forecast_3d    : float  -- forecasted precipitation, next 3 days (mm)
        soil_moisture  : float  -- latest soil moisture 0-7 cm (m3/m3, 0-1)
    None on any failure.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_sum",
        "hourly": "soil_moisture_0_to_1cm",
        "past_days": 7,
        "forecast_days": 3,
        "timezone": "Asia/Phnom_Penh",
    }

    try:
        resp = requests.get(WEATHER_URL, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        print(f"  [open_meteo] weather request failed for ({lat}, {lon}): {exc}")
        return None

    try:
        daily_precip = data["daily"]["precipitation_sum"]  # list of floats

        # daily_precip covers past_days (7) + forecast_days (3) = 10 entries.
        # Index 0..6 = past 7 days (oldest first), 7..9 = forecast 3 days.
        past_7 = [v if v is not None else 0.0 for v in daily_precip[:7]]
        forecast = [v if v is not None else 0.0 for v in daily_precip[7:10]]

        rainfall_24h = past_7[-1]            # most recent full day
        rainfall_3d = sum(past_7[-3:])        # last 3 days
        rainfall_7d = sum(past_7)             # last 7 days
        forecast_3d = sum(forecast)           # next 3 days

        # Soil moisture -- grab latest available hourly value.
        soil_values = data.get("hourly", {}).get("soil_moisture_0_to_1cm", [])
        soil_moisture = None
        for v in reversed(soil_values):
            if v is not None:
                soil_moisture = v
                break
        if soil_moisture is None:
            soil_moisture = 0.0

        return {
            "rainfall_24h": round(rainfall_24h, 2),
            "rainfall_3d": round(rainfall_3d, 2),
            "rainfall_7d": round(rainfall_7d, 2),
            "forecast_3d": round(forecast_3d, 2),
            "soil_moisture": round(soil_moisture, 3),
        }

    except (KeyError, IndexError, TypeError) as exc:
        print(f"  [open_meteo] failed to parse weather response: {exc}")
        return None


def fetch_river_discharge(lat: float, lon: float) -> float | None:
    """Fetch current river discharge estimate from Open-Meteo Flood API.

    Returns the most recent daily discharge value (m3/s), or None on failure.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "river_discharge",
        "past_days": 7,
        "forecast_days": 1,
    }

    try:
        resp = requests.get(FLOOD_URL, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        print(f"  [open_meteo] flood request failed for ({lat}, {lon}): {exc}")
        return None

    try:
        discharge_values = data["daily"]["river_discharge"]
        # Return the most recent non-None value.
        for v in reversed(discharge_values):
            if v is not None:
                return round(v, 2)
        return None
    except (KeyError, IndexError, TypeError) as exc:
        print(f"  [open_meteo] failed to parse flood response: {exc}")
        return None
