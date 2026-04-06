# FloodKH — Cambodia Flood Monitor 🌊

## ប្រព័ន្ធតាមដានទឹកជំនន់កម្ពុជា

[![Update Flood Data](https://github.com/kalim/FloodKH/actions/workflows/update.yml/badge.svg)](https://github.com/kalim/FloodKH/actions/workflows/update.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub Pages](https://img.shields.io/badge/demo-live-brightgreen)](https://kalim.github.io/FloodKH)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)

Real-time flood monitoring and prediction dashboard for Cambodia. Tracks rainfall, soil moisture, and river discharge across 25 locations to provide early flood warnings.

---

## Motivation

Cambodia faces severe flooding annually, particularly during the monsoon season (June--November). The Mekong River and Tonle Sap Lake system creates a vast floodplain that makes millions of people vulnerable to rising waters each year. Existing early-warning systems are often inaccessible, fragmented, or delayed.

**FloodKH** is an open-source tool that provides accessible, transparent flood risk monitoring. By combining freely available satellite and weather data with a simple classification model, it delivers near-real-time flood status updates through a lightweight web dashboard -- no proprietary software or expensive infrastructure required.

---

## Live Demo

[kalim.github.io/FloodKH](https://kalim.github.io/FloodKH)

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Data APIs   │────▶│ Python       │────▶│  Static JSON    │
│  Open-Meteo  │     │ Scraper      │     │  flood_status   │
│  NASA GPM    │     │ + Classifier │     │  flood_history  │
│  GloFAS      │     └──────────────┘     └────────┬────────┘
└─────────────┘            ▲                       │
                           │                       ▼
                    ┌──────────────┐     ┌─────────────────┐
                    │ GitHub       │     │  GitHub Pages   │
                    │ Actions      │     │  Leaflet Map    │
                    │ (every 6h)   │     │  Dashboard      │
                    └──────────────┘     └─────────────────┘
```

1. **Data APIs** -- Open-Meteo, NASA GPM, and GloFAS provide rainfall, soil moisture, and river discharge data.
2. **Python Scraper + Classifier** -- Fetches the latest data for 25 Cambodian locations and computes a flood risk score.
3. **Static JSON** -- Results are written to `flood_status.json` and `flood_history.json`.
4. **GitHub Actions** -- A scheduled workflow runs the scraper every 6 hours and commits updated data.
5. **GitHub Pages** -- A Leaflet-based map dashboard reads the JSON files and renders an interactive flood map.

---

## Features

- **25 monitored locations** across Cambodia, covering major cities, river towns, and flood-prone areas
- **Multi-source data fusion** -- combines rainfall, soil moisture, and river discharge into a single risk score
- **4-level classification** -- Normal, Watch, Warning, Danger with clear color coding
- **Interactive Leaflet map** -- click any marker for detailed metrics and historical trends
- **Historical tracking** -- maintains a rolling history of flood status changes
- **Fully automated** -- GitHub Actions updates data every 6 hours with zero manual intervention
- **Zero-cost hosting** -- runs entirely on GitHub Pages and free API tiers
- **Bilingual support** -- Khmer and English labels

---

## Data Sources

| Source | Data | Resolution | Link |
|--------|------|------------|------|
| **Open-Meteo** | Rainfall, temperature, soil moisture | Hourly, 1 km | [open-meteo.com](https://open-meteo.com/) |
| **NASA GPM** | Satellite precipitation estimates | 30-min, 0.1 deg | [gpm.nasa.gov](https://gpm.nasa.gov/) |
| **GloFAS (Copernicus)** | River discharge forecasts | Daily, 0.05 deg | [globalfloods.eu](https://www.globalfloods.eu/) |

All data sources are free and publicly accessible. No API keys are required for basic usage.

---

## Classification Methodology

Each location receives a **flood risk score** (0--100) computed from three weighted components:

| Component | Weight | Metric |
|-----------|--------|--------|
| Rainfall intensity | 40% | Cumulative precipitation over 24h and 72h windows |
| Soil moisture | 30% | Volumetric water content at 0--10 cm depth |
| River discharge | 30% | Current discharge vs. historical return periods |

The score maps to four risk levels:

| Score | Level | Color | Meaning |
|-------|-------|-------|---------|
| 0--25 | **Normal** | Green | No flood risk |
| 26--50 | **Watch** | Yellow | Elevated conditions, monitor closely |
| 51--75 | **Warning** | Orange | Flooding likely, take precautions |
| 76--100 | **Danger** | Red | Severe flooding expected or occurring |

Thresholds are calibrated against historical flood events from the Mekong River Commission records.

---

## How to Run Locally

```bash
# Clone the repository
git clone https://github.com/kalim/FloodKH.git
cd FloodKH

# Install Python dependencies
pip install -r requirements.txt

# Run the scraper to fetch latest data
python -m scraper.main

# Open the dashboard in your browser
# Open docs/index.html in browser
```

**Requirements:** Python 3.11+ and an internet connection (to fetch data from APIs).

---

## Project Structure

```
FloodKH/
├── .github/workflows/
│   └── update.yml          # Scheduled GitHub Actions workflow
├── data/
│   ├── flood_status.json   # Current flood status (generated)
│   └── flood_history.json  # Historical records (generated)
├── docs/
│   ├── index.html          # Dashboard frontend
│   ├── data/               # JSON served via GitHub Pages
│   ├── css/
│   └── js/
├── scraper/
│   ├── __init__.py
│   ├── main.py             # Entry point
│   ├── classifier.py       # Flood risk scoring
│   ├── locations.py        # 25 monitored locations
│   └── sources/            # API client modules
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Contributing

Contributions are welcome. Here are some ways to help:

1. **Report issues** -- If you find a bug or have a suggestion, open an issue.
2. **Add locations** -- Propose new monitoring points by editing `scraper/locations.py`.
3. **Improve the model** -- Help refine the classification thresholds with ground-truth flood data.
4. **Translate** -- Help improve Khmer translations in the dashboard.
5. **Frontend improvements** -- Enhance the dashboard UI or add new visualizations.

To contribute code:

```bash
# Fork and clone
git clone https://github.com/<your-username>/FloodKH.git
cd FloodKH

# Create a feature branch
git checkout -b feature/your-feature

# Make changes, then submit a pull request
```

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## Credits & Acknowledgments

- **[Open-Meteo](https://open-meteo.com/)** -- Free weather and climate API
- **[NASA GPM](https://gpm.nasa.gov/)** -- Global Precipitation Measurement mission
- **[GloFAS (Copernicus)](https://www.globalfloods.eu/)** -- Global Flood Awareness System
- **[Mekong River Commission](https://www.mrcmekong.org/)** -- Historical flood data and basin information
- **[Leaflet](https://leafletjs.com/)** -- Open-source interactive maps
- **[OpenStreetMap](https://www.openstreetmap.org/)** -- Map tile data

Built with the goal of making flood information accessible to everyone in Cambodia.
