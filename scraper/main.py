"""
FloodKH -- Scraper orchestrator.

Iterates over all 25 Cambodia locations, fetches data from every configured
source, classifies flood risk, and writes:
    data/flood_status.json   -- latest snapshot for all locations
    data/flood_history.json  -- daily append (keeps last 90 days)
"""

import os
import sys
from datetime import datetime, timezone

# Resolve paths relative to this file so the script works from anywhere.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Make sure the project root is on sys.path for imports.
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scraper.locations import LOCATIONS
from scraper.sources.open_meteo import fetch_weather_data, fetch_river_discharge
from scraper.sources.nasa_gpm import fetch_precipitation as fetch_gpm
from scraper.sources.glofas import fetch_flood_alerts
from scraper.classifier import classify_risk
from scraper.utils import get_current_utc_time, safe_round, load_json, save_json


HISTORY_MAX_DAYS = 90
STATUS_FILE = os.path.join(DATA_DIR, "flood_status.json")
HISTORY_FILE = os.path.join(DATA_DIR, "flood_history.json")


def _process_location(loc: dict) -> dict:
    """Fetch all data sources and classify risk for one location."""
    name = loc["name"]
    lat, lon = loc["lat"], loc["lon"]

    print(f"  Processing {name} ({lat}, {lon}) ...")

    # --- Open-Meteo weather (primary source) ---
    weather = fetch_weather_data(lat, lon)
    rainfall_24h = weather["rainfall_24h"] if weather else None
    rainfall_3d = weather["rainfall_3d"] if weather else None
    rainfall_7d = weather["rainfall_7d"] if weather else None
    forecast_3d = weather["forecast_3d"] if weather else None
    soil_moisture = weather["soil_moisture"] if weather else None

    # --- Open-Meteo river discharge ---
    discharge = fetch_river_discharge(lat, lon)

    # --- NASA GPM (fallback for rainfall) ---
    gpm = fetch_gpm(lat, lon)
    # If Open-Meteo rainfall is missing, attempt GPM fill-in.
    if rainfall_24h is None and gpm and "precipitation_mm_hr" in gpm:
        rainfall_24h = safe_round(gpm["precipitation_mm_hr"] * 24, 2)

    # --- GloFAS flood alerts ---
    glofas_alert = fetch_flood_alerts(lat, lon)

    # --- Build classifier input ---
    classifier_input = {
        "rainfall_24h": rainfall_24h,
        "rainfall_3d": rainfall_3d,
        "rainfall_7d": rainfall_7d,
        "forecast_3d": forecast_3d,
        "soil_moisture": soil_moisture,
        "river_discharge": discharge,
        "river_discharge_avg": loc["river_discharge_avg_m3s"],
        "elevation_m": loc["elevation_m"],
        "proximity_mekong": loc["proximity_mekong"],
    }

    result = classify_risk(classifier_input)

    return {
        "name": loc["name"],
        "name_km": loc["name_km"],
        "province": loc["province"],
        "lat": loc["lat"],
        "lon": loc["lon"],
        "elevation_m": loc["elevation_m"],
        "proximity_mekong": loc["proximity_mekong"],
        "data": {
            "rainfall_24h_mm": safe_round(rainfall_24h),
            "rainfall_3d_mm": safe_round(rainfall_3d),
            "rainfall_7d_mm": safe_round(rainfall_7d),
            "forecast_3d_mm": safe_round(forecast_3d),
            "soil_moisture": safe_round(soil_moisture, 3),
            "river_discharge_m3s": safe_round(discharge),
            "river_discharge_avg_m3s": loc["river_discharge_avg_m3s"],
        },
        "risk": {
            "level": result["risk_level"],
            "score": result["risk_score"],
            "factors": result["factors"],
        },
        "sources": {
            "open_meteo_weather": weather is not None,
            "open_meteo_flood": discharge is not None,
            "nasa_gpm": gpm is not None,
            "glofas": glofas_alert is not None,
        },
        "glofas_alert": glofas_alert,
    }


def _update_history(current_date: str, locations_summary: list) -> None:
    """Append today's summary to flood_history.json, trimming to 90 days."""
    history = load_json(HISTORY_FILE)
    if not isinstance(history, list):
        history = []

    # Build a compact daily entry.
    daily_entry = {
        "date": current_date,
        "locations": [
            {
                "name": loc["name"],
                "risk_level": loc["risk"]["level"],
                "risk_score": loc["risk"]["score"],
                "rainfall_24h_mm": loc["data"]["rainfall_24h_mm"],
            }
            for loc in locations_summary
        ],
    }

    # Remove any existing entry for the same date (re-run idempotency).
    history = [h for h in history if h.get("date") != current_date]
    history.append(daily_entry)

    # Keep only the most recent HISTORY_MAX_DAYS entries.
    history = history[-HISTORY_MAX_DAYS:]

    save_json(HISTORY_FILE, history)
    print(f"  History updated ({len(history)} day(s) stored).")


def run() -> None:
    """Main entry point: fetch, classify, and save for all locations."""
    print("=" * 60)
    print("FloodKH scraper run started")
    print("=" * 60)

    timestamp = get_current_utc_time()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    results = []
    for loc in LOCATIONS:
        try:
            entry = _process_location(loc)
            results.append(entry)
        except Exception as exc:
            print(f"  ERROR processing {loc['name']}: {exc}")
            # Append a minimal failure record so the location is not silently
            # dropped from the output.
            results.append({
                "name": loc["name"],
                "name_km": loc["name_km"],
                "province": loc["province"],
                "lat": loc["lat"],
                "lon": loc["lon"],
                "elevation_m": loc["elevation_m"],
                "proximity_mekong": loc["proximity_mekong"],
                "data": {},
                "risk": {"level": "UNKNOWN", "score": 0, "factors": [str(exc)]},
                "sources": {
                    "open_meteo_weather": False,
                    "open_meteo_flood": False,
                    "nasa_gpm": False,
                    "glofas": False,
                },
                "glofas_alert": None,
            })

    # --- Aggregate statistics ---
    levels = [r["risk"]["level"] for r in results]
    summary = {
        "total_locations": len(results),
        "critical": levels.count("CRITICAL"),
        "high": levels.count("HIGH"),
        "moderate": levels.count("MODERATE"),
        "low": levels.count("LOW"),
        "unknown": levels.count("UNKNOWN"),
    }

    flood_status = {
        "generated_at": timestamp,
        "date": today,
        "summary": summary,
        "locations": results,
    }

    # --- Write outputs ---
    os.makedirs(DATA_DIR, exist_ok=True)
    save_json(STATUS_FILE, flood_status)
    print(f"\nStatus written to {STATUS_FILE}")

    _update_history(today, results)
    print(f"History written to {HISTORY_FILE}")

    # --- Final console summary ---
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  CRITICAL : {summary['critical']}")
    print(f"  HIGH     : {summary['high']}")
    print(f"  MODERATE : {summary['moderate']}")
    print(f"  LOW      : {summary['low']}")
    print(f"  UNKNOWN  : {summary['unknown']}")
    print("=" * 60)


if __name__ == "__main__":
    run()
