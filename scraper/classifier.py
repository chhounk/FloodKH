"""
FloodKH Classifier — Scores current flood risk for each Phnom Penh district.

Combines rainfall, soil moisture, river discharge, satellite data, and
static district vulnerability into a 0-100 risk score mapped to 4 alert levels.

Component breakdown (max 100):
    Rainfall        max 35  (25 observation + 10 forecast, +5 flash-flood bonus)
    Soil moisture   max 15  (12 base + 3 trend bonus)
    River discharge max 20  (15 base + 5 Tonle Sap reversal bonus)
    Satellite       max 15
    Vulnerability   max 15  (12 drainage + 3 history, capped)

Data contracts
--------------
weather_data : dict
    rainfall_7d_mm, rainfall_3d_mm, rainfall_24h_mm,
    forecast_24h_mm, forecast_48h_mm, forecast_72h_mm,
    intensity_mm_h (current hourly rate),
    soil_moisture (0-1), soil_moisture_deep (0-1),
    soil_trend ("rising" | "falling" | "stable" | None)

river_data : dict
    discharge_ratio (current / long-term avg for the month),
    tonle_sap_reverse (bool — is reversal active?)

satellite_data : dict
    flood_fraction_pct (% of district area flagged as inundated)
"""

from __future__ import annotations

from scraper.config import (
    ALERT_LABELS,
    ALERT_THRESHOLDS,
    DISCHARGE_RATIO_THRESHOLDS,
    DRAINAGE_QUALITY_SCORES,
    FLOOD_FRACTION_THRESHOLDS,
    FLOOD_HISTORY_MAX_BONUS,
    FORECAST_72H_THRESHOLDS,
    INTENSITY_FLASH_FLOOD_THRESHOLD,
    LOW_ELEVATION_BONUS,
    LOW_ELEVATION_THRESHOLD,
    RAINFALL_7D_THRESHOLDS,
    SOIL_MOISTURE_THRESHOLDS,
    SOIL_TREND_RISING_BONUS,
    TONLE_SAP_REVERSE_FLOW_BONUS,
)
from scraper.utils import clamp, safe_round, score_from_thresholds


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _safe_get(data: dict | None, key: str, default=None):
    """Safely retrieve a value from a dict that may be None."""
    if data is None:
        return default
    return data.get(key, default)


def _score_rainfall(weather_data: dict | None) -> tuple[int, list[str]]:
    """Score rainfall component (max 35). Returns (score, factors)."""
    factors: list[str] = []
    rainfall_7d = _safe_get(weather_data, "rainfall_7d_mm")
    forecast_72h_total = _compute_forecast_total(weather_data)
    intensity = _safe_get(weather_data, "intensity_mm_h")

    # 7-day accumulated rainfall (max 25)
    obs_score = score_from_thresholds(rainfall_7d, RAINFALL_7D_THRESHOLDS)

    # 72-hour forecast total (max 10)
    fcst_score = score_from_thresholds(forecast_72h_total, FORECAST_72H_THRESHOLDS)

    # Flash-flood intensity bonus (+5)
    flash_bonus = 0
    if intensity is not None and intensity >= INTENSITY_FLASH_FLOOD_THRESHOLD:
        flash_bonus = 5
        factors.append(f"Flash-flood intensity ({intensity:.0f} mm/h)")

    total = min(obs_score + fcst_score + flash_bonus, 35)

    # Build human-readable factors
    if rainfall_7d is not None:
        if obs_score >= 20:
            factors.append(f"Heavy rainfall ({rainfall_7d:.0f} mm in 7 days)")
        elif obs_score >= 12:
            factors.append(f"Moderate rainfall ({rainfall_7d:.0f} mm in 7 days)")
        elif obs_score == 0 and (forecast_72h_total or 0) < 20:
            factors.append("Low rainfall")

    if forecast_72h_total is not None and fcst_score >= 6:
        factors.append(f"Heavy rain forecast ({forecast_72h_total:.0f} mm in 72 h)")

    return total, factors


def _compute_forecast_total(weather_data: dict | None) -> float | None:
    """Sum the 24/48/72 h forecast values, returning None if all are missing."""
    vals = [
        _safe_get(weather_data, "forecast_24h_mm"),
        _safe_get(weather_data, "forecast_48h_mm"),
        _safe_get(weather_data, "forecast_72h_mm"),
    ]
    present = [v for v in vals if v is not None]
    return sum(present) if present else None


def _score_soil(weather_data: dict | None) -> tuple[int, list[str]]:
    """Score soil moisture component (max 15). Returns (score, factors)."""
    factors: list[str] = []
    sm = _safe_get(weather_data, "soil_moisture")
    trend = _safe_get(weather_data, "soil_trend")

    base = score_from_thresholds(sm, SOIL_MOISTURE_THRESHOLDS)
    bonus = SOIL_TREND_RISING_BONUS if trend == "rising" else 0
    total = min(base + bonus, 15)

    if sm is not None:
        if sm >= 0.85:
            factors.append(f"Soil near saturation ({sm * 100:.0f}%)")
        elif sm >= 0.7:
            factors.append(f"Soil moisture elevated ({sm * 100:.0f}%)")
        elif sm <= 0.3:
            factors.append("Dry soil conditions")

    if trend == "rising" and bonus > 0:
        factors.append("Soil moisture trend rising")

    return total, factors


def _score_river(river_data: dict | None) -> tuple[int, list[str]]:
    """Score river discharge component (max 20). Returns (score, factors)."""
    factors: list[str] = []
    ratio = _safe_get(river_data, "discharge_ratio")
    reverse = _safe_get(river_data, "tonle_sap_reverse", False)

    base = score_from_thresholds(ratio, DISCHARGE_RATIO_THRESHOLDS)
    bonus = TONLE_SAP_REVERSE_FLOW_BONUS if reverse else 0
    total = min(base + bonus, 20)

    if ratio is not None:
        if ratio >= 2.0:
            factors.append(f"River discharge critical ({ratio:.1f}\u00d7 average)")
        elif ratio >= 1.3:
            factors.append(f"River discharge elevated ({ratio:.1f}\u00d7 average)")

    if reverse:
        factors.append("Tonle Sap reverse flow active")

    return total, factors


def _score_satellite(satellite_data: dict | None) -> tuple[int, list[str]]:
    """Score satellite component (max 15). Returns (score, factors)."""
    factors: list[str] = []
    fraction = _safe_get(satellite_data, "flood_fraction_pct")

    total = score_from_thresholds(fraction, FLOOD_FRACTION_THRESHOLDS)

    if fraction is not None and fraction >= 5:
        factors.append(f"Satellite detects flooding ({fraction:.1f}% of area)")

    return total, factors


def _score_vulnerability(district: dict) -> tuple[int, list[str]]:
    """Score static district vulnerability (max 15). Returns (score, factors)."""
    factors: list[str] = []

    drainage = district.get("drainage_quality", 3)
    history = district.get("flood_history_rating", 1)
    elevation = district.get("elevation_m", 12)

    drain_score = DRAINAGE_QUALITY_SCORES.get(drainage, 6)
    history_bonus = round(FLOOD_HISTORY_MAX_BONUS * (history / 5))
    elev_bonus = LOW_ELEVATION_BONUS if elevation < LOW_ELEVATION_THRESHOLD else 0

    total = min(drain_score + history_bonus + elev_bonus, 15)

    if drainage <= 2:
        factors.append("Poor drainage infrastructure")
    if elevation < LOW_ELEVATION_THRESHOLD:
        factors.append(f"Low elevation ({elevation:.1f} m)")
    if history >= 4:
        factors.append("High flood history area")

    return total, factors


def _determine_alert_level(score: int) -> int:
    """Map a 0-100 composite score to an alert level (0-3)."""
    for level, (lo, hi) in ALERT_THRESHOLDS.items():
        if lo <= score <= hi:
            return level
    return 3  # anything above 100 is emergency


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def classify_district(
    district: dict,
    weather_data: dict | None = None,
    river_data: dict | None = None,
    satellite_data: dict | None = None,
) -> dict:
    """Compute the current flood risk classification for a single district.

    Parameters
    ----------
    district : dict
        A district record from :pymod:`scraper.districts`.
    weather_data : dict or None
        Rainfall observations, forecasts, soil moisture. Keys described in
        the module docstring.
    river_data : dict or None
        River discharge ratio and Tonle Sap reversal flag.
    satellite_data : dict or None
        Flood fraction percentage from satellite imagery.

    Returns
    -------
    dict
        Classification result containing alert level, score, component
        breakdown, human-readable factors, and key observation values.
    """
    all_factors: list[str] = []

    rainfall_score, rainfall_factors = _score_rainfall(weather_data)
    soil_score, soil_factors = _score_soil(weather_data)
    river_score, river_factors = _score_river(river_data)
    sat_score, sat_factors = _score_satellite(satellite_data)
    vuln_score, vuln_factors = _score_vulnerability(district)

    all_factors.extend(rainfall_factors)
    all_factors.extend(soil_factors)
    all_factors.extend(river_factors)
    all_factors.extend(sat_factors)
    all_factors.extend(vuln_factors)

    raw_score = rainfall_score + soil_score + river_score + sat_score + vuln_score
    score = int(clamp(raw_score, 0, 100))
    level = _determine_alert_level(score)

    # If nothing notable, add a reassuring default factor.
    if not all_factors:
        all_factors.append("Dry conditions")

    return {
        "district_id": district.get("id"),
        "level": level,
        "label": ALERT_LABELS.get(level, "UNKNOWN"),
        "score": score,
        "component_scores": {
            "rainfall": rainfall_score,
            "soil": soil_score,
            "river": river_score,
            "satellite": sat_score,
            "vulnerability": vuln_score,
        },
        "factors": all_factors,
        # Pass-through observation values for downstream consumers.
        "rainfall_24h_mm": safe_round(_safe_get(weather_data, "rainfall_24h_mm")),
        "rainfall_3d_mm": safe_round(_safe_get(weather_data, "rainfall_3d_mm")),
        "rainfall_7d_mm": safe_round(_safe_get(weather_data, "rainfall_7d_mm")),
        "forecast_24h_mm": safe_round(_safe_get(weather_data, "forecast_24h_mm")),
        "forecast_48h_mm": safe_round(_safe_get(weather_data, "forecast_48h_mm")),
        "forecast_72h_mm": safe_round(_safe_get(weather_data, "forecast_72h_mm")),
        "soil_moisture": safe_round(_safe_get(weather_data, "soil_moisture")),
        "soil_moisture_deep": safe_round(_safe_get(weather_data, "soil_moisture_deep")),
        "river_discharge_ratio": safe_round(_safe_get(river_data, "discharge_ratio")),
    }
