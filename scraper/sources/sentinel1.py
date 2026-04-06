"""
Sentinel-1 SAR (Synthetic Aperture Radar) data source.
Detects water extent through clouds using radar backscatter.

Source: Copernicus Dataspace Ecosystem
Product: GRD IW mode, VV+VH polarization
Water detection: VV backscatter < -15 dB

STATUS: STUB — Returns simulated data derived from rainfall levels.
TODO: Implement Copernicus Dataspace OData API integration.
"""
import random
from datetime import datetime, timezone, timedelta

# Drainage quality per district (1=poor, 5=excellent)
# Lower quality = more flood-prone
DRAINAGE_QUALITY = {
    "chamkarmon": 4,
    "daunkeo": 2,
    "prampirmeakkakra": 3,
    "tuolkouk": 3,
    "dangkao": 1,
    "meanchey": 2,
    "russeikeo": 2,
    "sensok": 2,
    "poursenchey": 2,
    "chrouychangvar": 1,
    "preysor": 1,
    "chbarmorn": 3,
    "stiungmeanchey": 2,
}

# Relative elevation modifier (0.0 = lowest, 1.0 = highest)
ELEVATION_MODIFIER = {
    "chamkarmon": 0.7,
    "daunkeo": 0.3,
    "prampirmeakkakra": 0.6,
    "tuolkouk": 0.5,
    "dangkao": 0.2,
    "meanchey": 0.4,
    "russeikeo": 0.3,
    "sensok": 0.3,
    "poursenchey": 0.3,
    "chrouychangvar": 0.1,
    "preysor": 0.1,
    "chbarmorn": 0.5,
    "stiungmeanchey": 0.3,
}


def fetch_flood_extent(bbox, district_polygons=None, rainfall_data=None):
    """
    Fetch latest Sentinel-1 scene and calculate flood fraction per district.

    Args:
        bbox: dict with north, south, east, west
        district_polygons: optional GeoJSON for per-district calculation
        rainfall_data: optional dict of district_id -> rainfall_7d_mm
                       (used by stub to simulate flood extent)

    Returns dict per district_id:
    {
        "chamkarmon": {
            "flood_fraction_pct": 2.1,
            "scene_date": "2026-04-05T06:00:00Z",
            "source": "simulated"
        }
    }

    Returns None on failure.
    """
    try:
        if rainfall_data is None:
            rainfall_data = {}

        now = datetime.now(timezone.utc)
        # Simulate a scene acquired earlier today or yesterday
        scene_time = now - timedelta(hours=random.randint(6, 30))
        scene_date = scene_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        results = {}
        districts = rainfall_data.keys() if rainfall_data else DRAINAGE_QUALITY.keys()

        for district_id in districts:
            rain_7d = rainfall_data.get(district_id, 0.0)
            drainage = DRAINAGE_QUALITY.get(district_id, 3)
            elevation = ELEVATION_MODIFIER.get(district_id, 0.5)

            # Base flood fraction from rainfall intensity
            base_fraction = _rainfall_to_flood_fraction(rain_7d)

            # Drainage vulnerability modifier: worse drainage = more flooding
            drainage_mod = (6 - drainage) / 5.0
            adjusted = base_fraction * drainage_mod

            # Elevation modifier: lower elevation = more flooding
            elevation_mod = 1.0 + (1.0 - elevation) * 0.5
            adjusted *= elevation_mod

            # Clamp to 0-100%
            adjusted = max(0.0, min(100.0, adjusted))

            results[district_id] = {
                "flood_fraction_pct": round(adjusted, 2),
                "scene_date": scene_date,
                "source": "simulated",
            }

        return results

    except Exception as e:
        print(f"[Sentinel-1] Error generating simulated data: {e}")
        return None


def _rainfall_to_flood_fraction(rain_7d_mm):
    """Convert 7-day rainfall total to a base flood fraction percentage."""
    if rain_7d_mm < 30:
        return random.uniform(0.0, 2.0)
    elif rain_7d_mm < 80:
        return random.uniform(1.0, 5.0)
    elif rain_7d_mm < 150:
        return random.uniform(3.0, 10.0)
    elif rain_7d_mm < 250:
        return random.uniform(8.0, 20.0)
    else:
        return random.uniform(15.0, 35.0)


def _real_implementation():
    """
    Placeholder for the real Sentinel-1 implementation.
    NOT CALLED — documents the intended Copernicus Dataspace API flow.

    Steps:
    1. Authenticate with Copernicus Dataspace
       - POST to https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token
       - Use client credentials (COPERNICUS_CLIENT_ID, COPERNICUS_CLIENT_SECRET)
       - Obtain access_token for subsequent API calls

    2. Search for latest S1 GRD scene covering Phnom Penh bbox
       - Query OData catalog: https://catalogue.dataspace.copernicus.eu/odata/v1/Products
       - Filter: Collection/Name eq 'SENTINEL-1'
       - Filter: Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/Value eq 'GRD')
       - Filter: OData.CSC.Intersects(area=geography'SRID=4326;POLYGON((104.80 11.45, 105.00 11.45, 105.00 11.68, 104.80 11.68, 104.80 11.45))')
       - Order by ContentDate/Start desc, take top 1

    3. Download VV band
       - GET product zip from /odata/v1/Products({product_id})/$value
       - Extract VV polarization GeoTIFF from measurement/ folder

    4. Apply calibration to get sigma0 in dB
       - sigma0_dB = 10 * log10(DN^2 / calibration_LUT)
       - Use annotation XML for calibration lookup table

    5. Threshold at -15 dB to create water mask
       - water_mask = sigma0_dB < -15.0
       - Apply morphological opening (3x3) to remove speckle noise
       - Apply Lee filter for additional speckle reduction

    6. Calculate flood fraction per district polygon
       - Rasterize district polygons to match S1 grid
       - For each district: flood_fraction = count(water_pixels) / count(total_pixels) * 100

    7. Compare against dry-season baseline
       - Maintain a reference water mask from dry season (Jan-Feb)
       - Subtract baseline water bodies (rivers, lakes, ponds)
       - Report only anomalous water extent as flood fraction
    """
    pass
