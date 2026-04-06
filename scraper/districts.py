from __future__ import annotations

"""
FloodKH Districts — Static data for all 14 Phnom Penh districts (khan).

Each district entry contains geographic coordinates, elevation, river proximity,
infrastructure quality ratings, and historical flood frequency. These values
drive the vulnerability component of the flood risk score.

Rating scales:
    drainage_quality:    1 = poor ... 5 = excellent
    flood_history_rating: 1 = rare ... 5 = very frequent (almost every year)
    impervious_pct:      percentage of ground surface that is impervious (roads,
                         buildings, concrete) — higher values mean more runoff
"""

DISTRICTS = [
    {
        "id": "chamkarmon",
        "name": "Chamkarmon",
        "name_km": "ចំការមន",
        "lat": 11.5500,
        "lon": 104.9300,
        "elevation_m": 10.5,
        "river_proximity_km": 1.8,
        "drainage_quality": 3,
        "flood_history_rating": 3,
        "impervious_pct": 85,
    },
    {
        "id": "daun_penh",
        "name": "Daun Penh",
        "name_km": "ដូនពេញ",
        "lat": 11.5750,
        "lon": 104.9200,
        "elevation_m": 9.0,
        "river_proximity_km": 0.3,
        "drainage_quality": 2,
        "flood_history_rating": 3,
        "impervious_pct": 90,
    },
    {
        "id": "prampir_makara",
        "name": "Prampir Makara",
        "name_km": "ប្រាំពីរមករា",
        "lat": 11.5650,
        "lon": 104.9150,
        "elevation_m": 11.0,
        "river_proximity_km": 1.2,
        "drainage_quality": 3,
        "flood_history_rating": 2,
        "impervious_pct": 88,
    },
    {
        "id": "tuol_kork",
        "name": "Tuol Kork",
        "name_km": "ទួលគោក",
        "lat": 11.5800,
        "lon": 104.9000,
        "elevation_m": 12.0,
        "river_proximity_km": 2.5,
        "drainage_quality": 3,
        "flood_history_rating": 2,
        "impervious_pct": 80,
    },
    {
        "id": "dangkor",
        "name": "Dangkor",
        "name_km": "ដង្កោ",
        "lat": 11.4800,
        "lon": 104.8600,
        "elevation_m": 7.5,
        "river_proximity_km": 4.0,
        "drainage_quality": 1,
        "flood_history_rating": 5,
        "impervious_pct": 45,
    },
    {
        "id": "mean_chey",
        "name": "Mean Chey",
        "name_km": "មានជ័យ",
        "lat": 11.5200,
        "lon": 104.9500,
        "elevation_m": 8.0,
        "river_proximity_km": 1.5,
        "drainage_quality": 2,
        "flood_history_rating": 4,
        "impervious_pct": 70,
    },
    {
        "id": "russey_keo",
        "name": "Russey Keo",
        "name_km": "ឫស្សីកែវ",
        "lat": 11.6100,
        "lon": 104.8900,
        "elevation_m": 9.5,
        "river_proximity_km": 1.0,
        "drainage_quality": 2,
        "flood_history_rating": 3,
        "impervious_pct": 60,
    },
    {
        "id": "sen_sok",
        "name": "Sen Sok",
        "name_km": "សែនសុខ",
        "lat": 11.5900,
        "lon": 104.8500,
        "elevation_m": 11.5,
        "river_proximity_km": 3.5,
        "drainage_quality": 1,
        "flood_history_rating": 4,
        "impervious_pct": 55,
    },
    {
        "id": "pou_senchey",
        "name": "Pou Senchey",
        "name_km": "ពោធិ៍សែនជ័យ",
        "lat": 11.5500,
        "lon": 104.8500,
        "elevation_m": 10.0,
        "river_proximity_km": 3.0,
        "drainage_quality": 2,
        "flood_history_rating": 3,
        "impervious_pct": 65,
    },
    {
        "id": "chroy_changvar",
        "name": "Chroy Changvar",
        "name_km": "ជ្រោយចង្វារ",
        "lat": 11.6200,
        "lon": 104.9400,
        "elevation_m": 7.0,
        "river_proximity_km": 0.1,
        "drainage_quality": 2,
        "flood_history_rating": 4,
        "impervious_pct": 40,
    },
    {
        "id": "prek_pnov",
        "name": "Prek Pnov",
        "name_km": "ព្រែកព្នៅ",
        "lat": 11.6500,
        "lon": 104.8700,
        "elevation_m": 8.5,
        "river_proximity_km": 0.5,
        "drainage_quality": 1,
        "flood_history_rating": 5,
        "impervious_pct": 30,
    },
    {
        "id": "chbar_ampov",
        "name": "Chbar Ampov",
        "name_km": "ច្បារអំពៅ",
        "lat": 11.5100,
        "lon": 104.9700,
        "elevation_m": 6.5,
        "river_proximity_km": 0.2,
        "drainage_quality": 1,
        "flood_history_rating": 5,
        "impervious_pct": 50,
    },
    {
        "id": "kamboul",
        "name": "Kamboul",
        "name_km": "កំបូល",
        "lat": 11.5100,
        "lon": 104.8300,
        "elevation_m": 9.0,
        "river_proximity_km": 5.0,
        "drainage_quality": 1,
        "flood_history_rating": 4,
        "impervious_pct": 35,
    },
    {
        "id": "boeng_keng_kang",
        "name": "Boeng Keng Kang",
        "name_km": "បឹងកេងកង",
        "lat": 11.5450,
        "lon": 104.9250,
        "elevation_m": 11.0,
        "river_proximity_km": 1.5,
        "drainage_quality": 4,
        "flood_history_rating": 2,
        "impervious_pct": 90,
    },
]

# Build an index for fast lookup by district ID.
_DISTRICT_INDEX = {d["id"]: d for d in DISTRICTS}


def get_district(district_id: str) -> dict | None:
    """Return a single district dict by its ID, or None if not found."""
    return _DISTRICT_INDEX.get(district_id)


def get_all_districts() -> list[dict]:
    """Return the full list of Phnom Penh district dicts."""
    return list(DISTRICTS)
