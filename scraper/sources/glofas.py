"""
FloodKH -- GloFAS / Copernicus flood alert stub.

The Global Flood Awareness System (GloFAS) provides probabilistic flood
forecasts via the Copernicus Climate Data Store (CDS).

Setup instructions
------------------
1. Create a free CDS account:
   https://cds.climate.copernicus.eu/user/register

2. Install the CDS API client:
       pip install cdsapi

3. Create the file ~/.cdsapirc with your credentials:
       url: https://cds.climate.copernicus.eu/api/v2
       key: <your_uid>:<your_api_key>

4. Accepted dataset licence on CDS website for:
   "GloFAS seasonal forecast" / "GloFAS medium-range forecast"

The function below is a stub that returns None when the CDS client is not
available.  Replace the body with a real cdsapi.Client().retrieve() call
once credentials are configured.
"""

import requests

GLOFAS_WMS_URL = (
    "https://www.globalfloods.eu/glofas-maps/wms"
)

REQUEST_TIMEOUT = 20


def fetch_flood_alerts(lat: float, lon: float) -> dict | None:
    """Query GloFAS for current flood alert level near a coordinate.

    Parameters
    ----------
    lat, lon : float
        WGS-84 coordinates.

    Returns
    -------
    dict with keys:
        alert_level : str   ("green", "yellow", "orange", "red")
        return_period : int  (estimated return period in years, if available)
    or None if the service is unreachable / not configured.

    Notes
    -----
    This is a *stub*.  A full implementation would use either:
      - cdsapi to download GloFAS gridded forecasts and sample the cell, or
      - the GloFAS WMS/WFS endpoint to request point data.
    """
    # Attempt a lightweight WMS GetFeatureInfo request (public endpoint).
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.1.1",
        "REQUEST": "GetFeatureInfo",
        "LAYERS": "AccRainEGE_World",
        "QUERY_LAYERS": "AccRainEGE_World",
        "INFO_FORMAT": "application/json",
        "SRS": "EPSG:4326",
        "WIDTH": 1,
        "HEIGHT": 1,
        "X": 0,
        "Y": 0,
        "BBOX": f"{lon-0.05},{lat-0.05},{lon+0.05},{lat+0.05}",
    }

    try:
        resp = requests.get(GLOFAS_WMS_URL, params=params, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            # Service not available or endpoint changed -- degrade gracefully.
            return None
        data = resp.json()
        # Parse alert information from the response (structure varies).
        # Placeholder: real parsing logic would go here.
        return None
    except (requests.RequestException, ValueError) as exc:
        # Expected when GloFAS WMS is unreachable or credentials missing.
        print(f"  [glofas] request failed for ({lat}, {lon}): {exc}")
        return None
