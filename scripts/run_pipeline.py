"""
run_pipeline.py
===============
Runs the full ETL pipeline: acquire raw data → transform → export.

Outputs (all in data/clean/ and project root):
  • data/clean/combined_state.csv   – historical + recent economic data
  • data/clean/health_state.csv     – health infrastructure by state/year
  • data/clean/sdi_scores.csv       – SDI index (2022 reference year)
  • data/clean/dashboard_data.xlsx  – 3-sheet Excel workbook
  • malaysia_project.db             – SQLite database (3 tables)

Usage (from project root):
    python -m scripts.run_pipeline                  # full pipeline
    python -m scripts.run_pipeline --skip-acquire   # transform only (use existing raw data)
    python -m scripts.run_pipeline --force-acquire  # force re-download of raw data
"""

import argparse
import sys
import time

from scripts import acquire, transform


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Malaysia inequality ETL pipeline."
    )
    parser.add_argument(
        "--skip-acquire",
        action="store_true",
        help="Skip downloading raw data; use existing files in data/raw/.",
    )
    parser.add_argument(
        "--force-acquire",
        action="store_true",
        help="Re-download raw data even if files already exist.",
    )
    args = parser.parse_args()

    t0 = time.time()

    if not args.skip_acquire:
        print("\n========================================")
        print("  Step 1: Acquire")
        print("========================================")
        try:
            acquire.run(force=args.force_acquire)
        except RuntimeError as e:
            print(f"\n[FAIL] Acquire step failed: {e}")
            sys.exit(1)

    print("\n========================================")
    print("  Step 2: Transform + Export")
    print("========================================")
    try:
        transform.run()
    except Exception as e:
        print(f"\n[FAIL] Transform step failed: {e}")
        raise

    elapsed = time.time() - t0
    print(f"\n✓ Pipeline complete in {elapsed:.1f}s")
    print("  → Open data/clean/dashboard_data.xlsx in Excel")
    print("  → Connect Tableau to malaysia_project.db")


if __name__ == "__main__":
    main()
