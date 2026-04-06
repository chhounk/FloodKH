"""
Open-Meteo Weather API client.
Primary data source — free, no authentication required.
https://open-meteo.com/en/docs
"""
import requests
from datetime import datetime, timezone

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
HISTORY_URL = "https://archive-api.open-meteo.com/v1/archive"


def fetch_weather_data(lat, lon):
    """
    Fetch current + forecast weather data for a location.

    Returns dict with:
    - rainfall_24h_mm: observed last 24h
    - rainfall_3d_mm: observed last 3 days
    - rainfall_7d_mm: observed last 7 days
    - forecast_24h_mm: forecast next 24h
    - forecast_48h_mm: forecast next 24-48h
    - forecast_72h_mm: forecast next 48-72h
    - rainfall_intensity_max_mmh: peak hourly rate in forecast
    - soil_moisture_shallow: 0-7cm fraction
    - soil_moisture_deep: 7-28cm fraction
    - soil_saturation_trend: "rising", "stable", or "falling"
    - hourly_forecast: list of {time, precipitation_mm} for 72h

    Returns None on failure.
    """
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "precipitation,rain,soil_moisture_0_to_7cm,soil_moisture_7_to_28cm",
            "past_days": 14,
            "forecast_days": 7,
            "timezone": "UTC",
        }

        resp = requests.get(FORECAST_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        precip = hourly.get("precipitation", [])
        soil_shallow = hourly.get("soil_moisture_0_to_7cm", [])
        soil_deep = hourly.get("soil_moisture_7_to_28cm", [])

        if not times or not precip:
            print("[Open-Meteo] No hourly data returned")
            return None

        # Find the index of "now" — the last timestamp that is <= current UTC time
        now = datetime.now(timezone.utc)
        now_str = now.strftime("%Y-%m-%dT%H:%M")

        now_idx = 0
        for i, t in enumerate(times):
            if t <= now_str:
                now_idx = i
            else:
                break

        # Helper to safely sum a slice of precipitation values
        def safe_sum(values, start, end):
            sliced = values[max(start, 0):end]
            return round(sum(v for v in sliced if v is not None), 2)

        # --- Observed rainfall ---
        rainfall_24h = safe_sum(precip, now_idx - 23, now_idx + 1)
        rainfall_3d = safe_sum(precip, now_idx - 71, now_idx + 1)
        rainfall_7d = safe_sum(precip, now_idx - 167, now_idx + 1)

        # --- Forecast rainfall ---
        forecast_24h = safe_sum(precip, now_idx + 1, now_idx + 25)
        forecast_48h = safe_sum(precip, now_idx + 25, now_idx + 49)
        forecast_72h = safe_sum(precip, now_idx + 49, now_idx + 73)

        # --- Peak hourly intensity in forecast period ---
        forecast_slice = precip[now_idx + 1 : now_idx + 73]
        forecast_valid = [v for v in forecast_slice if v is not None]
        rainfall_intensity_max = round(max(forecast_valid), 2) if forecast_valid else 0.0

        # --- Soil moisture (latest available value) ---
        def latest_value(values, up_to_idx):
            for i in range(min(up_to_idx, len(values) - 1), -1, -1):
                if values[i] is not None:
                    return round(values[i], 4)
            return None

        sm_shallow = latest_value(soil_shallow, now_idx)
        sm_deep = latest_value(soil_deep, now_idx)

        # --- Soil saturation trend ---
        # Compare average of last 72h vs previous 72h for shallow moisture
        def avg_window(values, start, end):
            window = values[max(start, 0):end]
            valid = [v for v in window if v is not None]
            return sum(valid) / len(valid) if valid else None

        recent_avg = avg_window(soil_shallow, now_idx - 71, now_idx + 1)
        prior_avg = avg_window(soil_shallow, now_idx - 143, now_idx - 71)

        if recent_avg is not None and prior_avg is not None:
            diff = recent_avg - prior_avg
            if diff > 0.005:
                soil_trend = "rising"
            elif diff < -0.005:
                soil_trend = "falling"
            else:
                soil_trend = "stable"
        else:
            soil_trend = "stable"

        # --- Hourly forecast for next 72h ---
        hourly_forecast = []
        for i in range(now_idx + 1, min(now_idx + 73, len(times))):
            hourly_forecast.append({
                "time": times[i],
                "precipitation_mm": precip[i] if precip[i] is not None else 0.0,
            })

        return {
            "rainfall_24h_mm": rainfall_24h,
            "rainfall_3d_mm": rainfall_3d,
            "rainfall_7d_mm": rainfall_7d,
            "forecast_24h_mm": forecast_24h,
            "forecast_48h_mm": forecast_48h,
            "forecast_72h_mm": forecast_72h,
            "rainfall_intensity_max_mmh": rainfall_intensity_max,
            "soil_moisture_shallow": sm_shallow,
            "soil_moisture_deep": sm_deep,
            "soil_saturation_trend": soil_trend,
            "hourly_forecast": hourly_forecast,
        }

    except requests.exceptions.RequestException as e:
        print(f"[Open-Meteo] Request failed: {e}")
        return None
    except Exception as e:
        print(f"[Open-Meteo] Error processing data: {e}")
        return None
