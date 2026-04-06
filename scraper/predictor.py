"""
FloodKH Predictor — 72-hour flood risk forecast for Phnom Penh districts.

Generates risk predictions at T+0 (current), T+24 h, T+48 h, and T+72 h by
progressively substituting observed data with forecast values and extrapolated
trends.  Each future step carries increasing uncertainty.

Strategy per time step:
    Rainfall     — Replace 7-day observation with (obs + cumulative forecast).
    Soil moisture — Extrapolate trend: +0.05/day if rising, -0.03/day if falling.
    River        — Use forecast discharge ratio if available; else extrapolate.
    Satellite    — Held constant at T+0 (no satellite forecast available).

Confidence degrades with horizon:
    T+24 h  →  "high"
    T+48 h  →  "medium"
    T+72 h  →  "low"
"""

from __future__ import annotations

import copy
from typing import Callable

from scraper.classifier import classify_district
from scraper.config import UNCERTAINTY_PER_STEP
from scraper.utils import clamp


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SOIL_RISE_PER_DAY = 0.05
_SOIL_FALL_PER_DAY = 0.03
_SOIL_MAX = 0.95
_SOIL_MIN = 0.05

_CONFIDENCE_MAP = {
    1: "high",
    2: "medium",
    3: "low",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _project_weather(
    weather_data: dict | None,
    step: int,
) -> dict | None:
    """Build a projected weather dict for *step* days into the future.

    Parameters
    ----------
    weather_data : dict or None
        Current observations and forecasts.
    step : int
        Number of 24 h steps ahead (1, 2, or 3).

    Returns
    -------
    dict or None
        Modified copy of *weather_data* with rainfall and soil values
        adjusted for the forecast horizon.
    """
    if weather_data is None:
        return None

    projected = copy.deepcopy(weather_data)

    # --- Rainfall: add cumulative forecast to 7-day observation total ------
    base_7d = weather_data.get("rainfall_7d_mm") or 0.0
    cumulative_forecast = 0.0
    for i in range(1, step + 1):
        key = f"forecast_{i * 24}h_mm"
        cumulative_forecast += weather_data.get(key) or 0.0

    projected["rainfall_7d_mm"] = base_7d + cumulative_forecast

    # At future steps the "current 24 h" becomes the day's forecast.
    projected["rainfall_24h_mm"] = weather_data.get(f"forecast_{step * 24}h_mm")

    # The intensity is unknown for future steps; clear it.
    projected["intensity_mm_h"] = None

    # --- Soil moisture: extrapolate trend ----------------------------------
    sm = weather_data.get("soil_moisture")
    trend = weather_data.get("soil_trend")
    if sm is not None:
        if trend == "rising":
            sm = sm + _SOIL_RISE_PER_DAY * step
        elif trend == "falling":
            sm = sm - _SOIL_FALL_PER_DAY * step
        projected["soil_moisture"] = clamp(sm, _SOIL_MIN, _SOIL_MAX)

    sm_deep = weather_data.get("soil_moisture_deep")
    if sm_deep is not None:
        # Deep moisture responds more slowly — half the surface rate.
        if trend == "rising":
            sm_deep = sm_deep + (_SOIL_RISE_PER_DAY * 0.5) * step
        elif trend == "falling":
            sm_deep = sm_deep - (_SOIL_FALL_PER_DAY * 0.5) * step
        projected["soil_moisture_deep"] = clamp(sm_deep, _SOIL_MIN, _SOIL_MAX)

    return projected


def _project_river(
    river_data: dict | None,
    step: int,
) -> dict | None:
    """Build a projected river data dict for *step* days ahead.

    If forecast ratios are provided (``discharge_ratio_t24h``, etc.) they
    are used directly; otherwise the current ratio is extrapolated by
    assuming a 5 %/day increase when above average, or held constant.
    """
    if river_data is None:
        return None

    projected = copy.deepcopy(river_data)

    forecast_key = f"discharge_ratio_t{step * 24}h"
    if forecast_key in river_data and river_data[forecast_key] is not None:
        projected["discharge_ratio"] = river_data[forecast_key]
    else:
        ratio = river_data.get("discharge_ratio")
        if ratio is not None and ratio > 1.0:
            # Extrapolate a gentle rise when the river is already above avg.
            projected["discharge_ratio"] = ratio * (1 + 0.05 * step)
        # else: keep current ratio

    return projected


def _identify_key_driver(
    current_scores: dict,
    future_scores: dict,
) -> str:
    """Determine which component drove the largest score change."""
    max_delta = 0
    driver = "rainfall"  # default

    for component in ("rainfall", "soil", "river", "satellite", "vulnerability"):
        cur = current_scores.get(component, 0)
        fut = future_scores.get(component, 0)
        delta = fut - cur
        if delta > max_delta:
            max_delta = delta
            driver = component

    # Provide human-readable labels.
    labels = {
        "rainfall": "Forecast rainfall accumulation",
        "soil": "Rising soil moisture",
        "river": "Increasing river discharge",
        "satellite": "Expanding flood extent",
        "vulnerability": "District vulnerability",
    }
    return labels.get(driver, driver)


def _apply_uncertainty(score: int, step: int) -> tuple[int, int, int]:
    """Apply uncertainty band to a score.

    Returns
    -------
    tuple of (score, score_low, score_high)
        The central score (unchanged), and the lower/upper bounds of the
        uncertainty band.
    """
    margin = UNCERTAINTY_PER_STEP * step * score
    score_low = max(0, int(score - margin))
    score_high = min(100, int(score + margin))
    return score, score_low, score_high


def _level_from_score(score: int) -> tuple[int, str]:
    """Return (level, label) for a 0-100 score."""
    from scraper.config import ALERT_LABELS, ALERT_THRESHOLDS

    for level, (lo, hi) in ALERT_THRESHOLDS.items():
        if lo <= score <= hi:
            return level, ALERT_LABELS[level]
    return 3, ALERT_LABELS[3]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def predict_72h(
    district: dict,
    weather_data: dict | None = None,
    river_data: dict | None = None,
    satellite_data: dict | None = None,
    classifier_fn: Callable | None = None,
) -> dict:
    """Generate a 72-hour flood risk forecast for a single district.

    Parameters
    ----------
    district : dict
        A district record from :pymod:`scraper.districts`.
    weather_data : dict or None
        Current weather observations and forecasts.
    river_data : dict or None
        Current river discharge data.
    satellite_data : dict or None
        Current satellite flood-extent data.
    classifier_fn : callable or None
        The classification function.  Defaults to
        :pyfunc:`scraper.classifier.classify_district`.

    Returns
    -------
    dict
        Keys ``current``, ``t24h``, ``t48h``, ``t72h``.  The ``current``
        entry is the full classifier output.  Each future entry contains
        ``level``, ``label``, ``score``, ``score_low``, ``score_high``,
        ``confidence``, and ``key_driver``.
    """
    if classifier_fn is None:
        classifier_fn = classify_district

    # T+0 — classify with current data.
    current = classifier_fn(district, weather_data, river_data, satellite_data)
    current_scores = current["component_scores"]

    result = {"current": current}

    for step in (1, 2, 3):
        proj_weather = _project_weather(weather_data, step)
        proj_river = _project_river(river_data, step)
        # Satellite is held constant — no projection available.
        proj_satellite = satellite_data

        future = classifier_fn(district, proj_weather, proj_river, proj_satellite)
        future_score = future["score"]
        future_scores = future["component_scores"]

        score, score_low, score_high = _apply_uncertainty(future_score, step)
        level, label = _level_from_score(score)
        key_driver = _identify_key_driver(current_scores, future_scores)
        confidence = _CONFIDENCE_MAP.get(step, "low")

        horizon_key = f"t{step * 24}h"
        result[horizon_key] = {
            "level": level,
            "label": label,
            "score": score,
            "score_low": score_low,
            "score_high": score_high,
            "confidence": confidence,
            "key_driver": key_driver,
            "component_scores": future_scores,
            "factors": future["factors"],
        }

    return result
