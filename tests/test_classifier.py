"""Tests for the FloodKH classifier."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.classifier import classify_district


def test_normal_conditions():
    """Dry season, low everything -> NORMAL (level 0)."""
    district = {
        "id": "chamkarmon", "elevation_m": 10.5, "river_proximity_km": 1.8,
        "drainage_quality": 3, "flood_history_rating": 3, "impervious_pct": 85,
    }
    weather = {
        "rainfall_24h_mm": 2.0, "rainfall_3d_mm": 5.0, "rainfall_7d_mm": 15.0,
        "forecast_24h_mm": 3.0, "forecast_48h_mm": 5.0, "forecast_72h_mm": 2.0,
        "intensity_mm_h": 5.0,
        "soil_moisture": 0.20, "soil_moisture_deep": 0.25, "soil_trend": "stable",
    }
    river = {"discharge_ratio": 0.7}
    satellite = {"flood_fraction_pct": 0.5}

    result = classify_district(district, weather, river, satellite)
    assert result["level"] == 0, f"Expected NORMAL, got level {result['level']} (score {result['score']})"
    assert result["score"] <= 20


def test_watch_conditions():
    """Moderate rain on vulnerable district -> WATCH (level 1)."""
    district = {
        "id": "chbar_ampov", "elevation_m": 6.5, "river_proximity_km": 0.2,
        "drainage_quality": 1, "flood_history_rating": 5, "impervious_pct": 50,
    }
    weather = {
        "rainfall_24h_mm": 15.0, "rainfall_3d_mm": 30.0, "rainfall_7d_mm": 50.0,
        "forecast_24h_mm": 10.0, "forecast_48h_mm": 8.0, "forecast_72h_mm": 5.0,
        "intensity_mm_h": 10.0,
        "soil_moisture": 0.40, "soil_moisture_deep": 0.35, "soil_trend": "stable",
    }
    river = {"discharge_ratio": 1.0}
    satellite = {"flood_fraction_pct": 1.5}

    result = classify_district(district, weather, river, satellite)
    assert result["level"] == 1, f"Expected WATCH, got level {result['level']} (score {result['score']})"
    assert 21 <= result["score"] <= 45


def test_warning_conditions():
    """Heavy rain, saturated soil, rising rivers -> WARNING (level 2)."""
    district = {
        "id": "dangkor", "elevation_m": 7.5, "river_proximity_km": 4.0,
        "drainage_quality": 1, "flood_history_rating": 5, "impervious_pct": 45,
    }
    weather = {
        "rainfall_24h_mm": 40.0, "rainfall_3d_mm": 100.0, "rainfall_7d_mm": 160.0,
        "forecast_24h_mm": 25.0, "forecast_48h_mm": 15.0, "forecast_72h_mm": 10.0,
        "intensity_mm_h": 20.0,
        "soil_moisture": 0.65, "soil_moisture_deep": 0.60, "soil_trend": "rising",
    }
    river = {"discharge_ratio": 1.4}
    satellite = {"flood_fraction_pct": 6.0}

    result = classify_district(district, weather, river, satellite)
    assert result["level"] == 2, f"Expected WARNING, got level {result['level']} (score {result['score']})"
    assert 46 <= result["score"] <= 70


def test_emergency_conditions():
    """Extreme everything -> EMERGENCY (level 3)."""
    district = {
        "id": "chbar_ampov", "elevation_m": 6.5, "river_proximity_km": 0.2,
        "drainage_quality": 1, "flood_history_rating": 5, "impervious_pct": 50,
    }
    weather = {
        "rainfall_24h_mm": 120.0, "rainfall_3d_mm": 280.0, "rainfall_7d_mm": 400.0,
        "forecast_24h_mm": 80.0, "forecast_48h_mm": 60.0, "forecast_72h_mm": 40.0,
        "intensity_mm_h": 45.0,
        "soil_moisture": 0.92, "soil_moisture_deep": 0.88, "soil_trend": "rising",
    }
    river = {"discharge_ratio": 2.2}
    satellite = {"flood_fraction_pct": 25.0}

    result = classify_district(district, weather, river, satellite)
    assert result["level"] == 3, f"Expected EMERGENCY, got level {result['level']} (score {result['score']})"
    assert result["score"] >= 71


def test_missing_data_graceful():
    """Missing data sources should not crash."""
    district = {
        "id": "tuol_kork", "elevation_m": 12.0, "river_proximity_km": 2.5,
        "drainage_quality": 3, "flood_history_rating": 2, "impervious_pct": 80,
    }
    weather = {
        "rainfall_24h_mm": 10.0, "rainfall_3d_mm": 25.0, "rainfall_7d_mm": 50.0,
        "forecast_24h_mm": 15.0, "forecast_48h_mm": 10.0, "forecast_72h_mm": 5.0,
        "intensity_mm_h": 8.0,
        "soil_moisture": 0.35, "soil_moisture_deep": 0.30, "soil_trend": "stable",
    }
    result = classify_district(district, weather, None, None)
    assert result["level"] >= 0
    assert "score" in result


if __name__ == "__main__":
    test_normal_conditions()
    test_watch_conditions()
    test_warning_conditions()
    test_emergency_conditions()
    test_missing_data_graceful()
    print("All classifier tests passed!")
