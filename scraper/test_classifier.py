"""
FloodKH -- Tests for the risk classifier.

Run with:
    python -m pytest scraper/test_classifier.py -v
or:
    python scraper/test_classifier.py
"""

import sys
import os
from unittest.mock import patch
from datetime import datetime, timezone

# Ensure project root is importable.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.classifier import classify_risk


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _base_data(**overrides) -> dict:
    """Return a baseline data dict with safe defaults, applying overrides."""
    base = {
        "rainfall_24h": 0.0,
        "rainfall_3d": 0.0,
        "rainfall_7d": 0.0,
        "forecast_3d": 0.0,
        "soil_moisture": 0.0,
        "river_discharge": 100.0,
        "river_discharge_avg": 200.0,
        "elevation_m": 150.0,
        "proximity_mekong": 0.0,
    }
    base.update(overrides)
    return base


def _classify_in_dry_season(data: dict) -> dict:
    """Run classifier while forcing month to February (dry season)."""
    fake_now = datetime(2025, 2, 15, tzinfo=timezone.utc)
    with patch("scraper.classifier.datetime") as mock_dt:
        mock_dt.now.return_value = fake_now
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        return classify_risk(data)


def _classify_in_wet_season(data: dict) -> dict:
    """Run classifier while forcing month to August (wet season)."""
    fake_now = datetime(2025, 8, 15, tzinfo=timezone.utc)
    with patch("scraper.classifier.datetime") as mock_dt:
        mock_dt.now.return_value = fake_now
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        return classify_risk(data)


# ---------------------------------------------------------------------------
# Test scenarios
# ---------------------------------------------------------------------------

def test_low_risk_dry_conditions():
    """Dry conditions, high elevation, far from Mekong -> LOW."""
    data = _base_data(
        rainfall_24h=2.0,
        rainfall_3d=5.0,
        rainfall_7d=10.0,
        forecast_3d=3.0,
        soil_moisture=0.2,
        river_discharge=50.0,
        river_discharge_avg=200.0,
        elevation_m=150.0,
        proximity_mekong=0.1,
    )
    result = _classify_in_dry_season(data)
    assert result["risk_level"] == "LOW", f"Expected LOW, got {result}"
    assert result["risk_score"] <= 25


def test_moderate_risk_some_rain():
    """Moderate rain and soil moisture -> MODERATE."""
    data = _base_data(
        rainfall_24h=25.0,   # 10 pts
        rainfall_3d=60.0,    # 15 pts
        rainfall_7d=80.0,    # 5 pts
        forecast_3d=15.0,    # 5 pts
        soil_moisture=0.4,   # 5 pts
        river_discharge=180.0,
        river_discharge_avg=200.0,  # ratio 0.9 -> 5 pts
        elevation_m=80.0,    # 5 pts
        proximity_mekong=0.3,
    )
    # Sum = 10+15+5+5+5+5+5 = 50 -> MODERATE (26-50)
    result = _classify_in_dry_season(data)
    assert result["risk_level"] == "MODERATE", f"Expected MODERATE, got {result}"
    assert 26 <= result["risk_score"] <= 50


def test_high_risk_heavy_rain():
    """Heavy rain + saturated soil -> HIGH."""
    data = _base_data(
        rainfall_24h=70.0,   # 20 pts
        rainfall_3d=120.0,   # 25 pts
        rainfall_7d=150.0,   # 10 pts
        forecast_3d=40.0,    # 5 pts
        soil_moisture=0.75,  # 15 pts
        river_discharge=250.0,
        river_discharge_avg=200.0,  # ratio 1.25 -> 10 pts
        elevation_m=15.0,    # 15 pts
        proximity_mekong=0.5,
    )
    # Sum = 20+25+10+5+15+10+15 = 100 -> well above 51, but let's
    # check without wet-season and without Mekong bonus.
    # Actually 100 would be CRITICAL.  Adjust to target HIGH range.
    data["rainfall_24h"] = 55.0   # 20 pts
    data["rainfall_3d"] = 55.0    # 15 pts
    data["rainfall_7d"] = 40.0    # 5 pts
    data["forecast_3d"] = 12.0    # 5 pts
    data["soil_moisture"] = 0.55  # 10 pts
    # ratio still 1.25 -> 10 pts
    # elevation 15 -> 15 pts
    # Total = 20+15+5+5+10+10+15 = 80 -> CRITICAL.  Hmm.
    # Let's lower elevation.
    data["elevation_m"] = 60.0    # 5 pts
    # Total = 20+15+5+5+10+10+5 = 70 -> HIGH (51-75)
    result = _classify_in_dry_season(data)
    assert result["risk_level"] == "HIGH", f"Expected HIGH, got {result}"
    assert 51 <= result["risk_score"] <= 75


def test_critical_risk_extreme():
    """Extreme rainfall, saturated soil, high discharge -> CRITICAL."""
    data = _base_data(
        rainfall_24h=120.0,  # 30 pts
        rainfall_3d=250.0,   # 35 pts
        rainfall_7d=300.0,   # 20 pts
        forecast_3d=110.0,   # 25 pts
        soil_moisture=0.9,   # 20 pts
        river_discharge=400.0,
        river_discharge_avg=200.0,  # ratio 2.0 -> 25 pts
        elevation_m=8.0,     # 15 pts
        proximity_mekong=0.9,  # +10 bonus
    )
    # Base = 30+35+20+25+20+25+15 = 170.  No wet season -> 170 + 10 = 180.
    result = _classify_in_dry_season(data)
    assert result["risk_level"] == "CRITICAL", f"Expected CRITICAL, got {result}"
    assert result["risk_score"] >= 76


def test_wet_season_multiplier():
    """The same moderate input should score higher in the wet season."""
    data = _base_data(
        rainfall_24h=25.0,
        rainfall_3d=60.0,
        rainfall_7d=80.0,
        forecast_3d=15.0,
        soil_moisture=0.4,
        river_discharge=180.0,
        river_discharge_avg=200.0,
        elevation_m=80.0,
        proximity_mekong=0.3,
    )
    dry = _classify_in_dry_season(data)
    wet = _classify_in_wet_season(data)
    assert wet["risk_score"] > dry["risk_score"], (
        f"Wet score ({wet['risk_score']}) should exceed dry ({dry['risk_score']})"
    )


def test_mekong_proximity_bonus():
    """Proximity > 0.7 should add 10 points."""
    data_far = _base_data(proximity_mekong=0.3)
    data_near = _base_data(proximity_mekong=0.9)

    far = _classify_in_dry_season(data_far)
    near = _classify_in_dry_season(data_near)

    assert near["risk_score"] == far["risk_score"] + 10, (
        f"Near ({near['risk_score']}) should be far ({far['risk_score']}) + 10"
    )


def test_none_values_handled():
    """All None inputs should not crash and should produce LOW."""
    data = {
        "rainfall_24h": None,
        "rainfall_3d": None,
        "rainfall_7d": None,
        "forecast_3d": None,
        "soil_moisture": None,
        "river_discharge": None,
        "river_discharge_avg": None,
        "elevation_m": None,
        "proximity_mekong": None,
    }
    result = _classify_in_dry_season(data)
    assert result["risk_level"] == "LOW"


# ---------------------------------------------------------------------------
# Direct execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_low_risk_dry_conditions,
        test_moderate_risk_some_rain,
        test_high_risk_heavy_rain,
        test_critical_risk_extreme,
        test_wet_season_multiplier,
        test_mekong_proximity_bonus,
        test_none_values_handled,
    ]
    passed = 0
    for fn in tests:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
            passed += 1
        except AssertionError as exc:
            print(f"  FAIL  {fn.__name__}: {exc}")
        except Exception as exc:
            print(f"  ERROR {fn.__name__}: {exc}")
    print(f"\n{passed}/{len(tests)} tests passed.")
