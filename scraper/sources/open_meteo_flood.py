"""
Open-Meteo Flood API client.
Provides river discharge forecasts based on GloFAS data.
https://open-meteo.com/en/docs/flood-api
"""
import requests
from datetime import datetime, timezone

FLOOD_URL = "https://flood-api.open-meteo.com/v1/flood"


def fetch_river_discharge(lat, lon):
    """
    Fetch river discharge data for Mekong near Phnom Penh.

    Returns dict with:
    - discharge_current_m3s: latest available discharge
    - discharge_forecast_24h: forecast 24h
    - discharge_forecast_48h: forecast 48h
    - discharge_forecast_72h: forecast 72h
    - discharge_max_forecast: peak in forecast period

    Returns None on failure.
    """
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "river_discharge,river_discharge_mean,river_discharge_max",
            "past_days": 7,
            "forecast_days": 7,
        }

        resp = requests.get(FLOOD_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        daily = data.get("daily", {})
        times = daily.get("time", [])
        discharge = daily.get("river_discharge", [])
        discharge_mean = daily.get("river_discharge_mean", [])
        discharge_max = daily.get("river_discharge_max", [])

        if not times or not discharge:
            print("[Open-Meteo Flood] No daily discharge data returned — "
                  "location may not be near a modeled river")
            return None

        # Filter out None values and find today's index
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        today_idx = None
        for i, t in enumerate(times):
            if t == today_str:
                today_idx = i
                break

        if today_idx is None:
            # Fall back to the last date that is <= today
            for i, t in enumerate(times):
                if t <= today_str:
                    today_idx = i

        if today_idx is None:
            print("[Open-Meteo Flood] Could not locate today in time series")
            return None

        def safe_val(values, idx):
            if 0 <= idx < len(values) and values[idx] is not None:
                return round(values[idx], 2)
            return None

        current = safe_val(discharge, today_idx)
        forecast_24h = safe_val(discharge, today_idx + 1)
        forecast_48h = safe_val(discharge, today_idx + 2)
        forecast_72h = safe_val(discharge, today_idx + 3)

        # Peak discharge in the forecast period (today onward)
        forecast_values = [
            v for v in discharge[today_idx:] if v is not None
        ]
        max_forecast = round(max(forecast_values), 2) if forecast_values else None

        # Also check discharge_max if available
        max_daily_values = [
            v for v in discharge_max[today_idx:] if v is not None
        ]
        if max_daily_values:
            max_daily_peak = round(max(max_daily_values), 2)
            if max_forecast is None or max_daily_peak > max_forecast:
                max_forecast = max_daily_peak

        return {
            "discharge_current_m3s": current,
            "discharge_forecast_24h": forecast_24h,
            "discharge_forecast_48h": forecast_48h,
            "discharge_forecast_72h": forecast_72h,
            "discharge_max_forecast": max_forecast,
        }

    except requests.exceptions.RequestException as e:
        print(f"[Open-Meteo Flood] Request failed: {e}")
        return None
    except Exception as e:
        print(f"[Open-Meteo Flood] Error processing data: {e}")
        return None
