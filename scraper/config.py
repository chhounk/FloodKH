"""
FloodKH Configuration — Scoring thresholds, weights, and constants.

All values are calibrated for Phnom Penh's hydrological conditions.
The scoring system produces a composite 0-100 risk score from five
components: rainfall (max 35), soil moisture (max 15), river discharge
(max 20), satellite imagery (max 15), and district vulnerability (max 15).
"""

# ---------------------------------------------------------------------------
# Alert Level Thresholds
# ---------------------------------------------------------------------------
# Maps integer level to (min_score, max_score) inclusive range.
ALERT_THRESHOLDS = {
    0: (0, 20),    # NORMAL  — no action needed
    1: (21, 45),   # WATCH   — stay informed
    2: (46, 70),   # WARNING — prepare / possible evacuation
    3: (71, 100),  # EMERGENCY — immediate action required
}

ALERT_LABELS = {
    0: "NORMAL",
    1: "WATCH",
    2: "WARNING",
    3: "EMERGENCY",
}

# ---------------------------------------------------------------------------
# Rainfall Scoring (max 35 points)
# ---------------------------------------------------------------------------
# Phnom Penh averages ~1 400 mm/year.  Monsoon months (Jun-Oct) routinely
# deliver 50-80 mm/day; a 7-day total above 250 mm signals extreme risk.
#
# Each list entry is (upper_bound_mm, score).  The first entry whose upper
# bound exceeds the observed value determines the score.

RAINFALL_7D_THRESHOLDS = [
    (30, 0),               # < 30 mm over 7 days — normal even in wet season
    (80, 5),               # Light sustained rain
    (150, 12),             # Moderate — soil approaching saturation
    (250, 20),             # Heavy — ground saturated
    (float("inf"), 25),    # Extreme — major flood risk
]

FORECAST_72H_THRESHOLDS = [
    (20, 0),
    (50, 3),
    (100, 6),
    (float("inf"), 10),
]

# Instantaneous intensity above this value (mm/h) triggers a +5 flash-flood
# bonus on top of the normal rainfall score.
INTENSITY_FLASH_FLOOD_THRESHOLD = 30  # mm/h

# ---------------------------------------------------------------------------
# Soil Moisture Scoring (max 15 points)
# ---------------------------------------------------------------------------
# Soil moisture is expressed as volumetric water content (0.0 - 1.0).
SOIL_MOISTURE_THRESHOLDS = [
    (0.3, 0),
    (0.5, 3),
    (0.7, 7),
    (0.85, 11),
    (float("inf"), 15),
]

# If the soil moisture trend over the last 48 h is rising, add this bonus.
SOIL_TREND_RISING_BONUS = 3

# ---------------------------------------------------------------------------
# River Discharge Scoring (max 20 points)
# ---------------------------------------------------------------------------
# Mekong at Phnom Penh (Chaktomuk confluence):
#   Dry season  ~2 000 m³/s
#   Wet season  ~25 000+ m³/s at peak
#
# We score by ratio of current discharge to the long-term monthly average.
DISCHARGE_RATIO_THRESHOLDS = [
    (1.0, 0),
    (1.3, 4),
    (1.6, 9),
    (2.0, 15),
    (float("inf"), 20),
]

# The Tonle Sap reversal (Jun-Oct) pushes water back toward Phnom Penh,
# significantly raising flood risk even before the Mekong peaks.
TONLE_SAP_REVERSE_FLOW_BONUS = 5
TONLE_SAP_REVERSE_MONTHS = [6, 7, 8, 9, 10]

# ---------------------------------------------------------------------------
# Satellite Scoring (max 15 points)
# ---------------------------------------------------------------------------
# Flood fraction = percentage of the district area flagged as inundated.
FLOOD_FRACTION_THRESHOLDS = [
    (2, 0),
    (5, 4),
    (10, 8),
    (20, 12),
    (float("inf"), 15),
]

# ---------------------------------------------------------------------------
# District Vulnerability Scoring (max 15 points)
# ---------------------------------------------------------------------------
# Static score derived from drainage quality, flood history, and elevation.
DRAINAGE_QUALITY_SCORES = {
    1: 12,   # Poor drainage (filled wetlands, no canals)
    2: 9,
    3: 6,
    4: 3,
    5: 0,    # Excellent drainage
}

# Bonus scaled linearly from the district's flood_history_rating (1-5).
FLOOD_HISTORY_MAX_BONUS = 3

# Districts below this elevation get an additional fixed bonus.
LOW_ELEVATION_THRESHOLD = 10  # meters above sea level
LOW_ELEVATION_BONUS = 2

# ---------------------------------------------------------------------------
# Prediction Uncertainty
# ---------------------------------------------------------------------------
# Each 24 h forecast step increases uncertainty by this fraction of the score.
UNCERTAINTY_PER_STEP = 0.10  # 10 % per 24 h step

# ---------------------------------------------------------------------------
# Mekong Reference Discharge (m³/s at Phnom Penh)
# ---------------------------------------------------------------------------
MEKONG_AVG_DISCHARGE = 8000       # Annual average
MEKONG_DRY_SEASON_AVG = 2500      # Dec - May
MEKONG_WET_SEASON_AVG = 15000     # Jun - Nov

# ---------------------------------------------------------------------------
# Data Retention
# ---------------------------------------------------------------------------
HISTORY_RETENTION_DAYS = 90

# ---------------------------------------------------------------------------
# Phnom Penh Geographic Bounding Box
# ---------------------------------------------------------------------------
PP_BBOX = {
    "north": 11.68,
    "south": 11.45,
    "east": 105.00,
    "west": 104.80,
}
