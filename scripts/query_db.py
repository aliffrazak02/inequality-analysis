"""
query_db.py
===========
Small helper to run read-only SQL queries against malaysia_project.db.

Usage examples:
    python -m scripts.query_db "SELECT * FROM sdi_scores LIMIT 10"
    python -m scripts.query_db "SELECT state, sdi_score FROM sdi_scores" --out output.csv
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd

from scripts.config import DB_PATH


def _is_read_only(sql: str) -> bool:
    """Allow only read-oriented SQL statements for safe sharing usage."""
    first = sql.strip().split(None, 1)
    if not first:
        return False
    keyword = first[0].lower()
    return keyword in {"select", "with", "pragma", "explain"}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a read-only query against the project SQLite database."
    )
    parser.add_argument("sql", help="SQL query to execute.")
    parser.add_argument(
        "--db",
        type=Path,
        default=DB_PATH,
        help=f"Path to SQLite database (default: {DB_PATH}).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Optional CSV output path. If omitted, results print to terminal.",
    )
    args = parser.parse_args()

    if not _is_read_only(args.sql):
        raise SystemExit("Only read-only SQL is allowed (SELECT/WITH/PRAGMA/EXPLAIN).")

    if not args.db.exists():
        raise SystemExit(f"Database not found: {args.db}")

    with sqlite3.connect(args.db) as con:
        df = pd.read_sql_query(args.sql, con)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(args.out, index=False)
        print(f"Saved {len(df)} row(s) to {args.out}")
        return

    if df.empty:
        print("Query returned 0 rows.")
        return

    print(df.to_string(index=False))
    print(f"\nRows: {len(df)}")


if __name__ == "__main__":
    main()
