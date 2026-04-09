# Poverty, Income Inequality, and Health Outcomes Across Malaysian States

A reproducible data pipeline and analysis workflow studying inequality patterns across all 16 Malaysian states and federal territories.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/aliffrazak02/inequality-analysis)

---

## What This Project Does

This project combines income, poverty, and health data from official Malaysian and international sources to:

- Profile inequality across all 16 states and federal territories
- Build a composite **Social Deprivation Index (SDI)** that ranks states by combined socioeconomic disadvantage
- Identify states with co-occurring income poverty and poor health access ("double deprivation")
- Track how income trends have shifted from 2019 to 2024

The final outputs - final report notebook, interactive tableau dashboard and video presentation

---

## Data Sources

| Source | Data |
|---|---|
| [OpenDOSM](https://open.dosm.gov.my/) | Household income, poverty rates, Gini coefficients, CPI by state |
| [MoH Malaysia](https://github.com/MoH-Malaysia/data-resources-public) | Hospital beds and health facilities by state |
| [World Bank](https://data.worldbank.org/) | Life expectancy, infant mortality, health expenditure (national) |

---

## Project Structure

```
inequality-analysis/
├── notebook/
│   ├── 01_acquire_data.ipynb   # Download raw data from APIs
│   ├── 02_etl.ipynb            # Clean, normalise, and load into SQLite
│   ├── 03_eda.ipynb            # Exploratory analysis and charts
│   └── 04_sdi_analysis.ipynb   # SDI construction and sensitivity checks
├── scripts/
│   ├── acquire.py              # Data acquisition logic
│   ├── transform.py            # ETL transformations
│   ├── visualise.py            # Chart generation
│   ├── run_pipeline.py         # End-to-end pipeline runner
│   └── query_db.py             # CLI helper for querying the SQLite database
├── data/
│   ├── raw/                    # Downloaded source files (git-ignored)
│   └── clean/                  # Analysis-ready outputs
├── figures/                    # All generated charts (PNG)
├── docs/                       # Project documentation
└── malaysia_project.db         # SQLite database (all clean tables)
```

---

## Key Outputs

| File | Description |
|---|---|
| `data/clean/combined_state.csv` | Income, poverty, and Gini by state and year |
| `data/clean/health_state.csv` | Hospital beds and facilities by state |
| `data/clean/sdi_scores.csv` | SDI rankings for all 16 states |
| `data/clean/cpi_state.csv` | CPI inflation data by state |
| `data/clean/dashboard_data.xlsx` | All tables in a single Excel workbook |
| `malaysia_project.db` | SQLite database with all clean tables |

### SDI Weights

The Social Deprivation Index is computed from five indicators using the following weights:

| Indicator | Weight |
|---|---|
| Poverty rate | 25% |
| Income (inverse) | 25% |
| Gini coefficient | 20% |
| Hospital beds per capita | 15% |
| Health facilities per capita | 15% |

---

## Quickstart

### View notebooks in-browser (no setup)

Open any notebook directly on GitHub or paste the URL into [nbviewer.org](https://nbviewer.org/):

- [01_acquire_data.ipynb](notebook/01_acquire_data.ipynb)
- [02_etl.ipynb](notebook/02_etl.ipynb)
- [03_eda.ipynb](notebook/03_eda.ipynb)
- [04_sdi_analysis.ipynb](notebook/04_sdi_analysis.ipynb)
- <a href="docs/final_report.html" target="_blank" rel="noopener noreferrer">Final report (HTML)</a>


### Run locally

**Requirements:** Python 3.14+, [uv](https://docs.astral.sh/uv/)

```bash
git clone https://github.com/aliffrazak02/inequality-analysis.git
cd inequality-analysis
uv sync
uv run python -m scripts.run_pipeline
```

This will download raw data, run all ETL transforms, generate figures, and write all output files.

---

## SQLite Database

Open `malaysia_project.db` with any SQLite-compatible tool:

- [DB Browser for SQLite](https://sqlitebrowser.org/) (GUI)
- [DBeaver](https://dbeaver.io/) (GUI)
- Python `sqlite3` / pandas
- `sqlite3` CLI

**Tables:** `combined_state`, `health_state`, `sdi_scores`, `cpi_state`

### Query from the command line

Print results to terminal:

```bash
uv run python -m scripts.query_db "SELECT * FROM sdi_scores ORDER BY sdi_rank LIMIT 10"
```

Export to CSV:

```bash
uv run python -m scripts.query_db \
  "SELECT state, sdi_score FROM sdi_scores ORDER BY sdi_rank" \
  --out data/clean/top_sdi.csv
```

---
