# inequality-analysis

State-level inequality analysis for Malaysia, including ETL scripts, exploratory notebooks, and a shareable SQLite database.

## Access For Anyone

### 1) View notebooks in-browser (no setup)

Open the notebook files directly on GitHub:

- notebook/01_acquire_data.ipynb
- notebook/02_etl.ipynb
- notebook/03_eda.ipynb
- notebook/04_sdi_analysis.ipynb

GitHub renders notebook cells and outputs in the browser. To keep them easy to read for others, run all cells and commit saved outputs before pushing.

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

- docs/sqlite_quickstart.sql

## Reproducibility Checklist

Before sharing publicly:

1. Run the pipeline and ensure outputs are up to date.
2. Run notebook cells top-to-bottom.
3. Save notebook outputs.
4. Commit notebooks and malaysia_project.db.
5. Push to GitHub.

This ensures viewers can open notebooks immediately and query the same SQLite snapshot.
