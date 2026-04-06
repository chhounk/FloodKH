"""
FloodKH -- NASA GPM IMERG precipitation stub.

This module provides a placeholder for fetching near-real-time precipitation
data from NASA's Global Precipitation Measurement (GPM) mission via the
GES DISC (Goddard Earth Sciences Data and Information Services Center).

Dataset: GPM IMERG Late Run (half-hourly, 0.1-degree resolution)
    https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGHHL_06/summary

Cambodia bounding box (approximate):
    Latitude:  10.0 -- 14.7
    Longitude: 102.3 -- 107.7

Setup instructions
------------------
1. Create a free NASA Earthdata account:
   https://urs.earthdata.nasa.gov/users/new

2. Authorise GES DISC in your Earthdata profile:
   https://disc.gsfc.nasa.gov/earthdata-login

3. Create a ~/.netrc file (or use the requests auth param):
       machine urs.earthdata.nasa.gov
       login <your_username>
       password <your_password>

4. Set environment variable NASA_EARTHDATA_TOKEN for bearer-token auth
   (alternative to .netrc).

The function below sketches the real request structure but will gracefully
return None when credentials are unavailable.
"""

import os

import requests

# GES DISC OPeNDAP / CMR search endpoint for IMERG Late Run
IMERG_CMR_URL = (
    "https://cmr.earthdata.nasa.gov/search/granules.json"
)

# Cambodia bounding box
CAMBODIA_BBOX = {
    "lat_min": 10.0,
    "lat_max": 14.7,
    "lon_min": 102.3,
    "lon_max": 107.7,
}

REQUEST_TIMEOUT = 30


def fetch_precipitation(lat: float, lon: float) -> dict | None:
    """Attempt to fetch GPM IMERG precipitation for a point.

    Parameters
    ----------
    lat, lon : float
        WGS-84 coordinates (should fall within Cambodia bounding box).

    Returns
    -------
    dict with key ``precipitation_mm_hr`` (float) or None if unavailable.

    Notes
    -----
    This is a *stub*.  The full implementation requires NASA Earthdata
    credentials and non-trivial granule selection logic.  It is provided so
    the rest of the pipeline can call it without crashing.
    """
    token = os.environ.get("NASA_EARTHDATA_TOKEN")
    if not token:
        # No credentials configured -- skip silently.
        return None

    # Build a CMR search to find the latest IMERG granule covering the point.
    params = {
        "short_name": "GPM_3IMERGHHL",
        "version": "06",
        "point": f"{lon},{lat}",
        "sort_key": "-start_date",
        "page_size": 1,
    }
    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.get(
            IMERG_CMR_URL, params=params, headers=headers, timeout=REQUEST_TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()

        entries = data.get("feed", {}).get("entry", [])
        if not entries:
            return None

        # In a full implementation we would download the HDF5 granule and
        # extract the precipitation value at (lat, lon).  For now we return
        # None to indicate "data source contacted but extraction not
        # implemented".
        return None

    except (requests.RequestException, ValueError, KeyError) as exc:
        print(f"  [nasa_gpm] request failed for ({lat}, {lon}): {exc}")
        return None
