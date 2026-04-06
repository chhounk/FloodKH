"""
FloodKH Orchestrator — Fetches data from all sources, classifies risk,
generates 72-hour predictions, and saves output JSON files.
"""

from __future__ import annotations

import datetime
import logging
import sys

from scraper.classifier import classify_district
from scraper.config import (
    HISTORY_RETENTION_DAYS,
    MEKONG_AVG_DISCHARGE,
    MEKONG_DRY_SEASON_AVG,
    MEKONG_WET_SEASON_AVG,
    PP_BBOX,
    TONLE_SAP_REVERSE_MONTHS,
)
from scraper.districts import get_all_districts
from scraper.predictor import predict_72h
from scraper.sources.open_meteo import fetch_weather_data
from scraper.sources.open_meteo_flood import fetch_river_discharge
from scraper.sources.sentinel1 import fetch_flood_extent
from scraper.sources.sentinel2 import fetch_ndwi_extent
from scraper.sources.nasa_gpm import fetch_precipitation
from scraper.utils import get_utc_now, get_utc_now_str, load_json, save_json

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# Paths
DATA_DIR = "data"
PREDICTIONS_PATH = f"{DATA_DIR}/flood_predictions.json"
HISTORY_PATH = f"{DATA_DIR}/flood_history.json"


def _get_seasonal_avg_discharge() -> float:
    """Return the reference average discharge for the current month."""
    month = get_utc_now().month
    if month in TONLE_SAP_REVERSE_MONTHS:
        return MEKONG_WET_SEASON_AVG
    return MEKONG_DRY_SEASON_AVG


def _is_tonle_sap_reverse() -> bool:
    """Return True if the Tonle Sap reversal is expected (Jun-Oct)."""
    return get_utc_now().month in TONLE_SAP_REVERSE_MONTHS


def _build_weather_dict(raw: dict | None) -> dict | None:
    """Normalise Open-Meteo weather output to classifier field names."""
    if raw is None:
        return None
    return {
        "rainfall_24h_mm": raw.get("rainfall_24h_mm"),
        "rainfall_3d_mm": raw.get("rainfall_3d_mm"),
        "rainfall_7d_mm": raw.get("rainfall_7d_mm"),
        "forecast_24h_mm": raw.get("forecast_24h_mm"),
        "forecast_48h_mm": raw.get("forecast_48h_mm"),
        "forecast_72h_mm": raw.get("forecast_72h_mm"),
        "intensity_mm_h": raw.get("rainfall_intensity_max_mmh"),
        "soil_moisture": raw.get("soil_moisture_shallow"),
        "soil_moisture_deep": raw.get("soil_moisture_deep"),
        "soil_trend": raw.get("soil_saturation_trend"),
    }


def _build_river_dict(raw: dict | None) -> dict | None:
    """Normalise Open-Meteo flood output to classifier field names."""
    if raw is None:
        return None
    avg = _get_seasonal_avg_discharge()
    current = raw.get("discharge_current_m3s")
    ratio = current / avg if current and avg else None

    def _ratio(val):
        return val / avg if val and avg else ratio

    return {
        "discharge_ratio": ratio,
        "discharge_ratio_t24h": _ratio(raw.get("discharge_forecast_24h")),
        "discharge_ratio_t48h": _ratio(raw.get("discharge_forecast_48h")),
        "discharge_ratio_t72h": _ratio(raw.get("discharge_forecast_72h")),
        "tonle_sap_reverse": _is_tonle_sap_reverse(),
    }


def _build_satellite_dict(sentinel_data: dict | None, district_id: str) -> dict | None:
    """Extract per-district satellite data from the Sentinel-1 result."""
    if sentinel_data is None:
        return None
    entry = sentinel_data.get(district_id)
    if entry is None:
        return None
    return {"flood_fraction_pct": entry.get("flood_fraction_pct", 0)}


def run() -> None:
    """Main entry point — orchestrate data collection, classification, and output."""
    log.info("=== FloodKH Scraper Starting ===")

    districts = get_all_districts()
    now_str = get_utc_now_str()

    # --- Source status tracking ---
    source_status = {
        "open_meteo": "error",
        "sentinel_1": "stub",
        "sentinel_2": "stub",
        "nasa_gpm": "stub",
        "river_discharge": "error",
    }

    # --- Fetch river discharge once (same for all districts) ---
    log.info("Fetching river discharge data...")
    raw_river = fetch_river_discharge(11.57, 104.93)  # Chaktomuk confluence
    river_data = _build_river_dict(raw_river)
    if raw_river is not None:
        source_status["river_discharge"] = "ok"
        log.info("River discharge: %.1f m³/s", raw_river.get("discharge_current_m3s") or 0)
    else:
        log.warning("River discharge data unavailable")

    # --- Fetch satellite data (stubbed) ---
    log.info("Fetching satellite data (Sentinel-1 stub)...")
    # We'll pass rainfall_data after fetching weather; for now collect weather first
    weather_cache: dict[str, dict | None] = {}
    rainfall_for_sar: dict[str, float] = {}

    # --- Fetch weather data per district ---
    log.info("Fetching weather data for %d districts...", len(districts))
    om_success_count = 0
    for district in districts:
        did = district["id"]
        log.info("  %s (%s)...", district["name"], did)
        raw_weather = fetch_weather_data(district["lat"], district["lon"])
        weather_cache[did] = _build_weather_dict(raw_weather)
        if raw_weather is not None:
            om_success_count += 1
            rainfall_for_sar[did] = raw_weather.get("rainfall_7d_mm", 0)

    if om_success_count > 0:
        source_status["open_meteo"] = "ok"
    log.info("Open-Meteo: %d/%d districts fetched", om_success_count, len(districts))

    # Now fetch sentinel with rainfall context
    sentinel_data = fetch_flood_extent(PP_BBOX, rainfall_data=rainfall_for_sar)
    if sentinel_data:
        source_status["sentinel_1"] = "stub"  # Still stub even though it returns data

    # NASA GPM (stub)
    fetch_precipitation(PP_BBOX)

    # Sentinel-2 (stub)
    fetch_ndwi_extent(PP_BBOX)

    # --- Classify + predict per district ---
    log.info("Running classifier and 72h predictor...")
    output_districts = []
    level_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    t72_counts = {0: 0, 1: 0, 2: 0, 3: 0}

    for district in districts:
        did = district["id"]
        weather = weather_cache.get(did)
        sat = _build_satellite_dict(sentinel_data, did)

        try:
            prediction = predict_72h(district, weather, river_data, sat, classify_district)
        except Exception as e:
            log.error("  %s: prediction failed — %s", district["name"], e)
            continue

        current = prediction["current"]
        level_counts[current["level"]] += 1

        t72 = prediction.get("t72h", {})
        t72_counts[t72.get("level", 0)] += 1

        output_districts.append({
            "id": did,
            "name": district["name"],
            "name_km": district["name_km"],
            "lat": district["lat"],
            "lon": district["lon"],
            "current": current,
            "forecast": {
                "t24h": prediction["t24h"],
                "t48h": prediction["t48h"],
                "t72h": prediction["t72h"],
            },
        })

        level_label = current["label"]
        log.info("  %s: %s (score %d)", district["name"], level_label, current["score"])

    # --- Build output ---
    output = {
        "generated_at": now_str,
        "model_version": "1.0.0",
        "data_sources_status": source_status,
        "districts": output_districts,
        "city_summary": {
            "current": {
                "level_0": level_counts[0],
                "level_1": level_counts[1],
                "level_2": level_counts[2],
                "level_3": level_counts[3],
            },
            "t72h_worst_case": {
                "level_0": t72_counts[0],
                "level_1": t72_counts[1],
                "level_2": t72_counts[2],
                "level_3": t72_counts[3],
            },
        },
    }

    save_json(PREDICTIONS_PATH, output)
    log.info("Saved predictions to %s", PREDICTIONS_PATH)

    # --- Update history ---
    _update_history(output_districts, now_str)

    log.info("=== FloodKH Scraper Complete ===")
    log.info("Summary: L0=%d L1=%d L2=%d L3=%d",
             level_counts[0], level_counts[1], level_counts[2], level_counts[3])


def _update_history(districts: list[dict], timestamp: str) -> None:
    """Append today's snapshot to the rolling history file."""
    history = load_json(HISTORY_PATH)
    if "snapshots" not in history:
        history = {"snapshots": []}

    today = get_utc_now().strftime("%Y-%m-%d")

    # Build today's snapshot
    district_scores = {}
    for d in districts:
        current = d.get("current", {})
        district_scores[d["id"]] = {
            "level": current.get("level", 0),
            "score": current.get("score", 0),
        }

    snapshot = {"date": today, "districts": district_scores}

    # Replace today's entry if it already exists, else append
    existing_idx = None
    for i, s in enumerate(history["snapshots"]):
        if s.get("date") == today:
            existing_idx = i
            break

    if existing_idx is not None:
        history["snapshots"][existing_idx] = snapshot
    else:
        history["snapshots"].append(snapshot)

    # Trim to retention period
    cutoff = (get_utc_now() - datetime.timedelta(days=HISTORY_RETENTION_DAYS)).strftime("%Y-%m-%d")
    history["snapshots"] = [s for s in history["snapshots"] if s.get("date", "") >= cutoff]

    save_json(HISTORY_PATH, history)
    log.info("Updated history (%d snapshots)", len(history["snapshots"]))


if __name__ == "__main__":
    run()
