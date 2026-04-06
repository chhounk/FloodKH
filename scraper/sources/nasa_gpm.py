"""
NASA GPM IMERG precipitation data source.
Provides satellite-derived rainfall estimates independent of ground stations.

Product: GPM_3IMERGHHL (Half-Hourly Late Run)
Source: NASA GES DISC (https://disc.gsfc.nasa.gov/)
Auth: Requires NASA Earthdata account + bearer token

STATUS: STUB — Returns None. Set NASA_EARTHDATA_TOKEN env var to enable.
"""
import os


def fetch_precipitation(bbox):
    """
    Fetch IMERG precipitation data for Phnom Penh bounding box.

    Would return gridded precipitation data that can be aggregated per district.
    Currently returns None as NASA Earthdata authentication is not configured.

    To enable:
    1. Create account at https://urs.earthdata.nasa.gov/
    2. Approve GES DISC application
    3. Generate bearer token
    4. Set NASA_EARTHDATA_TOKEN environment variable
    """
    token = os.environ.get("NASA_EARTHDATA_TOKEN")
    if not token:
        print("[NASA GPM] No NASA_EARTHDATA_TOKEN set — skipping")
        return None

    # TODO: Implement OPeNDAP or GES DISC subset API call
    # Endpoint: https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGHHL_07/summary
    # Subset for Phnom Penh bbox: 104.80E-105.00E, 11.45N-11.68N
    print("[NASA GPM] API integration not yet implemented")
    return None
