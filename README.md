# FloodKH — Phnom Penh Flood Monitor

## ប្រព័ន្ធតាមដានទឹកជំនន់រាជធានីភ្នំពេញ

[![Update Flood Data](https://github.com/chhounk/FloodKH/actions/workflows/update.yml/badge.svg)](https://github.com/chhounk/FloodKH/actions/workflows/update.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Hyperlocal flood monitoring and **72-hour prediction system** for Phnom Penh's 14 districts. Combines weather data, satellite imagery, and hydrological indicators to provide early flood warnings.

## Why This Matters

Phnom Penh floods annually during the monsoon season (June–November). The Mekong, Tonle Sap, and Bassac rivers converge in the heart of the city at Chaktomuk. Districts like **Chbar Ampov**, **Dangkor**, **Prek Pnov**, and **Mean Chey** face severe flooding that displaces residents, damages infrastructure, and disrupts transport.

This open-source tool provides free, transparent, district-level flood risk monitoring with a 72-hour forecast horizon.

## Live Demo

🔗 [chhounk.github.io/FloodKH](https://chhounk.github.io/FloodKH)

## Architecture

```
Data Sources              Processing                    Output
─────────────            ──────────                    ──────
Open-Meteo ──────┐
                 ├──→ Python Scraper ──────────→ flood_predictions.json
Sentinel-1 SAR ──┤    + Classifier (0-100)       flood_history.json
                 ├──→ + 72h Predictor                     │
NASA GPM ────────┤                                        ▼
                 │    GitHub Actions              GitHub Pages
GloFAS ──────────┘    (every 6 hours)             Leaflet.js Map
                                                  + Dashboard
```

## Features

- **District-level monitoring** — 14 Phnom Penh districts with individual risk scores
- **72-hour prediction** — Forecast risk levels at T+24h, T+48h, T+72h
- **Interactive map** — Color-coded district polygons on a dark-themed Leaflet map
- **Timeline slider** — Visualize how risk evolves over the next 3 days
- **Multi-source data fusion** — Weather, river discharge, satellite imagery (stub), soil moisture
- **Bilingual** — English and Khmer (ខ្មែរ) language toggle
- **Mobile responsive** — Full-screen map with collapsible sidebar
- **Transparent methodology** — All scoring weights and thresholds documented

## Alert Levels

| Level | Label | Score | Description |
|-------|-------|-------|-------------|
| 🟢 0 | NORMAL | 0–20 | No flood risk |
| 🟡 1 | WATCH | 21–45 | Elevated conditions, monitor situation |
| 🟠 2 | WARNING | 46–70 | High flood risk, flooding likely |
| 🔴 3 | EMERGENCY | 71–100 | Critical, flooding imminent or active |

## Data Sources

| Source | Provides | Status | Frequency |
|--------|----------|--------|-----------|
| Open-Meteo | Precipitation, soil moisture, forecasts | **Live** | 6 hours |
| Open-Meteo Flood API | River discharge (GloFAS) | **Live** | Daily |
| Sentinel-1 SAR | Water extent detection | Stub | ~6 days |
| Sentinel-2 Optical | NDWI water index | Stub | ~5 days |
| NASA GPM IMERG | Satellite-derived rainfall | Stub | 30 min |

## Scoring Methodology

Five components contribute to the 0–100 composite score:

1. **Rainfall** (max 35 pts) — 7-day cumulative + 72h forecast + flash flood intensity
2. **Soil Moisture** (max 15 pts) — Current saturation level + trend
3. **River Discharge** (max 20 pts) — Current vs average ratio + Tonle Sap reversal bonus
4. **Satellite** (max 15 pts) — Flood fraction anomaly from SAR/optical
5. **District Vulnerability** (max 15 pts) — Drainage quality + flood history + elevation

See the [Methodology page](https://chhounk.github.io/FloodKH/methodology.html) for full details.

## Run Locally

```bash
git clone https://github.com/chhounk/FloodKH.git
cd FloodKH
pip install -r requirements.txt

# Run the scraper (fetches live data)
python -m scraper.main

# Copy data to frontend
cp data/flood_predictions.json docs/data/
cp data/flood_history.json docs/data/

# Open the dashboard
open docs/index.html
# or: python -m http.server 8000 -d docs
```

## Run Tests

```bash
python -m pytest tests/ -v
```

## Project Structure

```
FloodKH/
├── scraper/
│   ├── main.py              # Orchestrator
│   ├── classifier.py        # Current-state scoring engine
│   ├── predictor.py         # 72-hour forecast engine
│   ├── districts.py         # 14 Phnom Penh districts + static data
│   ├── config.py            # All thresholds and weights
│   ├── utils.py             # Shared utilities
│   └── sources/
│       ├── open_meteo.py        # Weather API (live)
│       ├── open_meteo_flood.py  # River discharge (live)
│       ├── sentinel1.py         # SAR water detection (stub)
│       ├── sentinel2.py         # Optical NDWI (stub)
│       └── nasa_gpm.py         # Satellite rainfall (stub)
├── data/
│   ├── flood_predictions.json
│   ├── flood_history.json
│   └── geojson/
├── docs/                    # GitHub Pages frontend
│   ├── index.html
│   ├── methodology.html
│   ├── css/style.css
│   └── js/
├── tests/
├── .github/workflows/
│   └── update.yml           # 6-hourly cron job
├── requirements.txt
├── README.md
└── LICENSE
```

## Roadmap

- [ ] Activate Sentinel-1 SAR integration (Copernicus Dataspace API)
- [ ] Add Sentinel-2 NDWI for optical confirmation
- [ ] NASA GPM IMERG integration for satellite rainfall
- [ ] Historical flood analysis and seasonal patterns
- [ ] ML model upgrade (gradient boosting on historical data)
- [ ] Push notifications for alert level changes
- [ ] Mobile-optimized PWA

## Contributing

Contributions are welcome! Please open an issue first to discuss proposed changes.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Push and open a Pull Request

## License

MIT License — see [LICENSE](LICENSE)

---

**Built by [Convergence](https://github.com/chhounk)**

Data: [Open-Meteo](https://open-meteo.com/), [Copernicus Sentinel](https://dataspace.copernicus.eu/), [NASA GPM](https://gpm.nasa.gov/), [GloFAS](https://www.globalfloods.eu/)
