"""
FloodKH -- Rule-based flood-risk classifier.

Scoring system
--------------
The classifier converts raw hydro-meteorological observations into a single
integer *risk score* and a human-readable *risk level*.

Weighted features and their point ranges:

    Feature                       | Thresholds (value -> points)
    ------------------------------|--------------------------------------
    rainfall_24h (mm)             | 0-5->0, 5-20->5, 20-50->10, 50-100->20, >100->30
    rainfall_3d  (mm)             | 0-10->0, 10-50->5, 50-100->15, 100-200->25, >200->35
    rainfall_7d  (mm)             | 0-30->0, 30-100->5, 100-200->10, >200->20
    forecast_3d  (mm)             | 0-10->0, 10-50->5, 50-100->15, >100->25
    soil_moisture (0-1)           | <0.3->0, 0.3-0.5->5, 0.5-0.7->10, 0.7-0.85->15, >0.85->20
    discharge_ratio (cur/avg)     | <0.8->0, 0.8-1.0->5, 1.0-1.3->10, 1.3-1.6->15, >1.6->25
    elevation_m                   | >100->0, 50-100->5, 20-50->10, <20->15

Modifiers applied *after* summing feature points:
    - Wet season (June--November): total *= 1.2
    - Mekong proximity > 0.7:     total += 10

Classification thresholds (on final score):
    LOW       0 -- 25
    MODERATE  26 -- 50
    HIGH      51 -- 75
    CRITICAL  76+
"""

from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Individual scoring functions
# ---------------------------------------------------------------------------

def _score_rainfall_24h(mm: float) -> int:
    if mm > 100:
        return 30
    if mm > 50:
        return 20
    if mm > 20:
        return 10
    if mm > 5:
        return 5
    return 0


def _score_rainfall_3d(mm: float) -> int:
    if mm > 200:
        return 35
    if mm > 100:
        return 25
    if mm > 50:
        return 15
    if mm > 10:
        return 5
    return 0


def _score_rainfall_7d(mm: float) -> int:
    if mm > 200:
        return 20
    if mm > 100:
        return 10
    if mm > 30:
        return 5
    return 0


def _score_forecast_3d(mm: float) -> int:
    if mm > 100:
        return 25
    if mm > 50:
        return 15
    if mm > 10:
        return 5
    return 0


def _score_soil_moisture(sm: float) -> int:
    if sm > 0.85:
        return 20
    if sm > 0.7:
        return 15
    if sm > 0.5:
        return 10
    if sm > 0.3:
        return 5
    return 0


def _score_discharge_ratio(ratio: float) -> int:
    if ratio > 1.6:
        return 25
    if ratio > 1.3:
        return 15
    if ratio > 1.0:
        return 10
    if ratio > 0.8:
        return 5
    return 0


def _score_elevation(elev_m: float) -> int:
    if elev_m < 20:
        return 15
    if elev_m < 50:
        return 10
    if elev_m <= 100:
        return 5
    return 0


# ---------------------------------------------------------------------------
# Risk-level thresholds
# ---------------------------------------------------------------------------

def _level_from_score(score: int) -> str:
    if score >= 76:
        return "CRITICAL"
    if score >= 51:
        return "HIGH"
    if score >= 26:
        return "MODERATE"
    return "LOW"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def classify_risk(data: dict) -> dict:
    """Classify flood risk for a single location.

    Parameters
    ----------
    data : dict
        Must contain the following keys (all numeric, may be None):
            rainfall_24h, rainfall_3d, rainfall_7d, forecast_3d,
            soil_moisture, river_discharge, river_discharge_avg,
            elevation_m, proximity_mekong

    Returns
    -------
    dict with keys:
        risk_level  : str   ("LOW", "MODERATE", "HIGH", "CRITICAL")
        risk_score  : int
        factors     : list[str]  -- human-readable breakdown
    """
    # Helper to safely treat None as 0.
    def v(key, default=0.0):
        val = data.get(key)
        return val if val is not None else default

    rainfall_24h = v("rainfall_24h")
    rainfall_3d = v("rainfall_3d")
    rainfall_7d = v("rainfall_7d")
    forecast_3d = v("forecast_3d")
    soil_moisture = v("soil_moisture")
    discharge = v("river_discharge")
    discharge_avg = v("river_discharge_avg", default=1.0)  # avoid div-by-zero
    elevation_m = v("elevation_m", default=100.0)
    proximity_mekong = v("proximity_mekong", default=0.0)

    # Compute discharge ratio.
    discharge_ratio = discharge / discharge_avg if discharge_avg > 0 else 0.0

    # Individual scores.
    s_r24 = _score_rainfall_24h(rainfall_24h)
    s_r3d = _score_rainfall_3d(rainfall_3d)
    s_r7d = _score_rainfall_7d(rainfall_7d)
    s_fc3 = _score_forecast_3d(forecast_3d)
    s_sm = _score_soil_moisture(soil_moisture)
    s_dr = _score_discharge_ratio(discharge_ratio)
    s_el = _score_elevation(elevation_m)

    total = s_r24 + s_r3d + s_r7d + s_fc3 + s_sm + s_dr + s_el

    factors = []

    # Wet-season modifier (June through November).
    now = datetime.now(timezone.utc)
    wet_season = 6 <= now.month <= 11
    if wet_season:
        total = int(total * 1.2)
        factors.append("Wet season multiplier applied (x1.2)")

    # Mekong proximity bonus.
    if proximity_mekong > 0.7:
        total += 10
        factors.append(f"Mekong proximity bonus +10 (proximity={proximity_mekong})")

    # Build human-readable factor list.
    factors.insert(0, f"Rainfall 24h: {rainfall_24h:.1f} mm -> {s_r24} pts")
    factors.insert(1, f"Rainfall 3d:  {rainfall_3d:.1f} mm -> {s_r3d} pts")
    factors.insert(2, f"Rainfall 7d:  {rainfall_7d:.1f} mm -> {s_r7d} pts")
    factors.insert(3, f"Forecast 3d:  {forecast_3d:.1f} mm -> {s_fc3} pts")
    factors.insert(4, f"Soil moisture: {soil_moisture:.3f} -> {s_sm} pts")
    factors.insert(5, f"Discharge ratio: {discharge_ratio:.2f} -> {s_dr} pts")
    factors.insert(6, f"Elevation: {elevation_m:.0f} m -> {s_el} pts")

    risk_level = _level_from_score(total)

    return {
        "risk_level": risk_level,
        "risk_score": total,
        "factors": factors,
    }
