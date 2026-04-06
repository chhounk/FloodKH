"""
Sentinel-2 Optical data source (supplementary).
Calculates NDWI (Normalized Difference Water Index) for water detection.

NDWI = (Band 3 Green - Band 8 NIR) / (Band 3 Green + Band 8 NIR)
Water: NDWI > 0.3

STATUS: STUB — Less reliable than SAR during monsoon due to cloud cover.
TODO: Implement Copernicus Dataspace API integration.
"""


def fetch_ndwi_extent(bbox):
    """
    Returns None — not yet implemented.
    Sentinel-2 is supplementary to Sentinel-1 SAR.
    During monsoon season, cloud cover typically exceeds 80%,
    making optical imagery unreliable for flood monitoring.
    """
    return None
