# Poverty, Income Inequality, and Health Outcomes Across Malaysian States

State-level inequality analysis for Malaysia, including ETL scripts, exploratory notebooks, and a shareable SQLite database.

## Project Overview

This project builds a reproducible data pipeline and analysis workflow to study inequality patterns across Malaysian states.

The project includes:

- Automated data acquisition from OpenDOSM, MoH Malaysia, and World Bank sources
- ETL transformation into clean, analysis-ready tables
- Exploratory and SDI-focused notebooks with charts and interpretation
- Export targets for analytics tools: CSV, Excel workbook, and SQLite database

Core outputs are designed to be easy to inspect, share, and reuse for dashboarding or further research.

## Access For Anyone

### 1) View notebooks in-browser (no setup)

Open the notebook files directly on GitHub:

- notebook/01_acquire_data.ipynb
- notebook/02_etl.ipynb
- notebook/03_eda.ipynb
- notebook/04_sdi_analysis.ipynb

### 1b) One-click Open in Colab

Use the badges below to open in Google Colab:

- Browse this repository in Colab (notebook picker)  
	[![Open Repo In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/aliffrazak02/inequality-analysis)

If GitHub rendering is slow, use nbviewer by pasting your notebook URL into:

- https://nbviewer.org/

### 2) Run locally with one command

Requirements:

- Python 3.14+
- uv (recommended) or pip

Install dependencies:

- uv sync

Run full pipeline (download raw data, transform, export):

- uv run python -m scripts.run_pipeline

Outputs:

- data/clean/combined_state.csv
- data/clean/health_state.csv
- data/clean/sdi_scores.csv
- data/clean/cpi_state.csv
- data/clean/dashboard_data.xlsx
- malaysia_project.db

## SQLite Database Access

Anyone can use the database with any SQLite-compatible tool:

- DB Browser for SQLite (GUI)
- DBeaver (GUI)
- Python sqlite3
- sqlite3 CLI

Main tables:

- combined_state
- health_state
- sdi_scores
- cpi_state

### Quick query via Python helper

Run a query and print results in terminal:

- uv run python -m scripts.query_db "SELECT * FROM sdi_scores ORDER BY sdi_rank LIMIT 10"

Export query results to CSV:

- uv run python -m scripts.query_db "SELECT state, sdi_score FROM sdi_scores ORDER BY sdi_rank" --out data/clean/top_sdi.csv

See more example queries in:

- [docs/sqlite_quickstart.sql](docs/sqlite_quickstart.sql)


