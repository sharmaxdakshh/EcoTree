# 🌳 EcoTree – Tree Inventory & Environmental Impact System

**EcoTree** is a full-fledged Python project for managing urban tree inventories, calculating environmental benefits (carbon sequestration, oxygen production, cooling effect), analyzing tree health, generating reports, and providing an interactive dashboard.

---

## Features

- **Tree Inventory Management** (SQLite + SQLAlchemy)
- **Environmental Calculations**
  - Annual CO₂ sequestration
  - Oxygen production
  - Cooling / energy-saving benefit
- **Health Scoring System** (0–100 + status categories)
- **Statistical Analysis** (zone-wise, species-wise)
- **Visualizations**
  - Static plots (Matplotlib / Seaborn)
  - Interactive Folium map
- **Professional PDF Report** (ReportLab)
- **CLI Interface** (Click)
- **Interactive Web Dashboard** (Streamlit)
- **Unit Tests**

---

## Project Structure

```
ecotree/
├── app/
│   └── streamlit_app.py          # Interactive dashboard
├── config/
│   └── config.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   └── images/
├── database/
│   └── trees.db                  # Created after `init`
├── notebooks/
├── outputs/
│   ├── maps/
│   ├── plots/
│   └── reports/
├── src/
│   ├── __init__.py
│   ├── analysis.py
│   ├── calculations.py
│   ├── data_loader.py
│   ├── database.py
│   ├── report_generator.py
│   └── visualization.py
├── tests/
│   └── test_calculations.py
├── main.py                       # CLI entry point
├── requirements.txt
└── README.md
```

---

## Installation

```bash
# Clone or navigate to the project
cd ecotree

# Create virtual environment
python -m venv venv

# Activate
# Linux / macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Quick Start

```bash
# 1. Initialize database + generate 800 sample trees
python main.py init

# 2. View summary statistics
python main.py summary

# 3. Zone performance
python main.py zones

# 4. Species impact
python main.py species

# 5. Critical trees needing attention
python main.py critical

# 6. Generate all plots
python main.py plots

# 7. Create interactive map
python main.py map

# 8. Generate professional PDF report
python main.py report

# 9. Run complete pipeline
python main.py all
```

### Launch Dashboard

```bash
streamlit run app/streamlit_app.py
```

---

## CLI Commands Overview

| Command              | Description                              |
|----------------------|------------------------------------------|
| `init`               | Create DB + sample data                  |
| `summary`            | High-level KPIs                          |
| `zones`              | Zone-wise table                          |
| `species`            | Species performance                      |
| `critical`           | List at-risk / critical trees            |
| `plots`              | Generate PNG charts                      |
| `map`                | Interactive HTML map                     |
| `report`             | Full PDF report                          |
| `all`                | Run plots + map + report together        |

---

## Sample Output Locations

- Plots → `outputs/plots/`
- Interactive map → `outputs/maps/tree_map.html`
- PDF report → `outputs/reports/ecotree_report.pdf`

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Technology Stack

- **Python 3.10+**
- pandas, numpy
- SQLAlchemy + SQLite
- Matplotlib, Seaborn, Folium
- scikit-learn (ready for extension)
- ReportLab
- Streamlit
- Click

---

## Extending the Project

Possible next steps:

1. Replace simulated health scores with real field inspection data
2. Add species-specific allometric equations (i-Tree style)
3. Integrate weather / drought stress API
4. Add image upload + basic disease detection
5. Multi-city comparison module
6. User authentication for the dashboard
7. Export to Excel / GeoJSON

---

## License

This project is provided for educational and portfolio purposes.

---

**Made for learning real-world Python application structure, data analysis, and environmental computing.**
