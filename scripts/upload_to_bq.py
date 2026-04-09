"""
upload_to_bq.py
===============
Upload cleaned CSV datasets to Google Cloud BigQuery.

Prerequisites:
    uv add google-cloud-bigquery python-dotenv db-dtypes

Usage:
    python scripts/upload_to_bq.py
    python scripts/upload_to_bq.py --tables combined_state sdi_scores
    python scripts/upload_to_bq.py --dry-run
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import pandas as pd
from google.cloud import bigquery
from google.cloud.bigquery import LoadJobConfig, WriteDisposition, SchemaField

# ---------------------------------------------------------------------------
# Load env
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

PROJECT_ID = os.environ["GCP_PROJECT_ID"]
DATASET_ID = os.getenv("BQ_DATASET_ID", "inequality_analysis")
LOCATION = os.getenv("GCP_LOCATION", "US")

# ---------------------------------------------------------------------------
# Table definitions: name -> (csv_path, bq_table_id, write_disposition)
# ---------------------------------------------------------------------------
TABLES = {
    "combined_state": {
        "path": ROOT / "data" / "clean" / "combined_state.csv",
        "table": f"{PROJECT_ID}.{DATASET_ID}.combined_state",
        "description": "Combined state-level income, poverty, Gini, and CPI data",
    },
    "sdi_scores": {
        "path": ROOT / "data" / "clean" / "sdi_scores.csv",
        "table": f"{PROJECT_ID}.{DATASET_ID}.sdi_scores",
        "description": "Social Deprivation Index scores by state",
    },
    "health_state": {
        "path": ROOT / "data" / "clean" / "health_state.csv",
        "table": f"{PROJECT_ID}.{DATASET_ID}.health_state",
        "description": "State-level health infrastructure data",
    },
    "cpi_national": {
        "path": ROOT / "data" / "clean" / "cpi_national.csv",
        "table": f"{PROJECT_ID}.{DATASET_ID}.cpi_national",
        "description": "National Consumer Price Index data",
    },
    "cpi_state": {
        "path": ROOT / "data" / "clean" / "cpi_state.csv",
        "table": f"{PROJECT_ID}.{DATASET_ID}.cpi_state",
        "description": "State-level Consumer Price Index data",
    },
}


def ensure_dataset(client: bigquery.Client) -> None:
    """Create the BigQuery dataset if it does not exist."""
    dataset_ref = bigquery.Dataset(f"{PROJECT_ID}.{DATASET_ID}")
    dataset_ref.location = LOCATION
    dataset_ref.description = "Malaysia inequality analysis — cleaned datasets"
    client.create_dataset(dataset_ref, exists_ok=True)
    print(f"Dataset ready: {PROJECT_ID}.{DATASET_ID}")


def upload_table(
    client: bigquery.Client,
    name: str,
    cfg: dict,
    dry_run: bool = False,
) -> None:
    """Load a single CSV into BigQuery, replacing existing data."""
    path: Path = cfg["path"]
    table_id: str = cfg["table"]

    if not path.exists():
        print(f"  [SKIP] {name}: file not found ({path})")
        return

    df = pd.read_csv(path)
    print(f"  {name}: {len(df):,} rows x {len(df.columns)} cols  →  {table_id}")

    if dry_run:
        print("    (dry-run — skipping upload)")
        return

    job_config = LoadJobConfig(
        write_disposition=WriteDisposition.WRITE_TRUNCATE,
        autodetect=True,
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()  # wait for completion

    table = client.get_table(table_id)
    print(f"    Loaded {table.num_rows:,} rows into {table_id}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload cleaned data to BigQuery")
    parser.add_argument(
        "--tables",
        nargs="+",
        choices=list(TABLES.keys()),
        default=list(TABLES.keys()),
        help="Which tables to upload (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Read CSVs and print row counts but do not upload",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    client = bigquery.Client(project=PROJECT_ID)

    if not args.dry_run:
        ensure_dataset(client)

    print(f"\nUploading {len(args.tables)} table(s) to {PROJECT_ID}.{DATASET_ID}\n")
    for name in args.tables:
        upload_table(client, name, TABLES[name], dry_run=args.dry_run)

    print("\nDone.")


if __name__ == "__main__":
    main()
