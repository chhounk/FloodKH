"""Tests for the FloodKH 72h predictor."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.predictor import predict_72h
from scraper.classifier import classify_district


def test_prediction_returns_all_timesteps():
    """Prediction should return current + 3 forecast steps."""
    district = {
        "id": "chamkarmon", "elevation_m": 10.5, "river_proximity_km": 1.8,
        "drainage_quality": 3, "flood_history_rating": 3, "impervious_pct": 85,
    }
    weather = {
        "rainfall_24h_mm": 5.0, "rainfall_3d_mm": 15.0, "rainfall_7d_mm": 30.0,
        "forecast_24h_mm": 20.0, "forecast_48h_mm": 25.0, "forecast_72h_mm": 15.0,
        "intensity_mm_h": 10.0,
        "soil_moisture": 0.30, "soil_moisture_deep": 0.35, "soil_trend": "stable",
    }
    river = {
        "discharge_ratio": 0.8,
        "discharge_ratio_t24h": 0.85,
        "discharge_ratio_t48h": 0.9,
        "discharge_ratio_t72h": 0.95,
    }
    satellite = {"flood_fraction_pct": 1.0}

    result = predict_72h(district, weather, river, satellite, classify_district)
    assert "current" in result
    assert "t24h" in result
    assert "t48h" in result
    assert "t72h" in result
    assert result["t24h"]["confidence"] == "high"
    assert result["t48h"]["confidence"] == "medium"
    assert result["t72h"]["confidence"] == "low"


def test_increasing_rain_escalates_risk():
    """Heavy forecast rain should increase risk over time."""
    district = {
        "id": "chbar_ampov", "elevation_m": 6.5, "river_proximity_km": 0.2,
        "drainage_quality": 1, "flood_history_rating": 5, "impervious_pct": 50,
    }
    weather = {
        "rainfall_24h_mm": 10.0, "rainfall_3d_mm": 25.0, "rainfall_7d_mm": 40.0,
        "forecast_24h_mm": 60.0, "forecast_48h_mm": 70.0, "forecast_72h_mm": 50.0,
        "intensity_mm_h": 10.0,
        "soil_moisture": 0.45, "soil_moisture_deep": 0.40, "soil_trend": "rising",
    }
    river = {
        "discharge_ratio": 1.0,
        "discharge_ratio_t24h": 1.2,
        "discharge_ratio_t48h": 1.4,
        "discharge_ratio_t72h": 1.6,
    }
    satellite = {"flood_fraction_pct": 2.0}

    result = predict_72h(district, weather, river, satellite, classify_district)
    assert result["t72h"]["score"] >= result["current"]["score"]


def test_prediction_with_none_sources():
    """Prediction should work with missing data sources."""
    district = {
        "id": "tuol_kork", "elevation_m": 12.0, "river_proximity_km": 2.5,
        "drainage_quality": 3, "flood_history_rating": 2, "impervious_pct": 80,
    }
    weather = {
        "rainfall_24h_mm": 5.0, "rainfall_3d_mm": 10.0, "rainfall_7d_mm": 20.0,
        "forecast_24h_mm": 8.0, "forecast_48h_mm": 6.0, "forecast_72h_mm": 4.0,
        "intensity_mm_h": 5.0,
        "soil_moisture": 0.25, "soil_moisture_deep": 0.30, "soil_trend": "stable",
    }
    result = predict_72h(district, weather, None, None, classify_district)
    assert "current" in result
    assert "t72h" in result


if __name__ == "__main__":
    test_prediction_returns_all_timesteps()
    test_increasing_rain_escalates_risk()
    test_prediction_with_none_sources()
    print("All predictor tests passed!")
