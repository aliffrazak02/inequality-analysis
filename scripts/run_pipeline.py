"""
run_pipeline.py
===============
Runs the full ETL pipeline: acquire raw data → transform → export → BigQuery.

Outputs (all in data/clean/ and project root):
  • data/clean/combined_state.csv   – historical + recent economic data
  • data/clean/health_state.csv     – health infrastructure by state/year
  • data/clean/sdi_scores.csv       – SDI index (2022 reference year)
  • data/clean/cpi_national.csv     – national CPI data
  • data/clean/dashboard_data.xlsx  – 4-sheet Excel workbook
  • malaysia_project.db             – SQLite database (4 tables)

  When --upload-bq is set, all clean tables are also pushed to BigQuery
  (requires GCP_PROJECT_ID in .env and valid Application Default Credentials).

Usage (from project root):
    python -m scripts.run_pipeline                       # acquire + transform
    python -m scripts.run_pipeline --upload-bq           # full pipeline + BigQuery upload
    python -m scripts.run_pipeline --skip-acquire        # transform only (use existing raw data)
    python -m scripts.run_pipeline --force-acquire       # force re-download of raw data
    python -m scripts.run_pipeline --upload-bq --dry-run # preview upload without writing to BQ
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
    parser.add_argument(
        "--upload-bq",
        action="store_true",
        help="Upload cleaned tables to Google BigQuery after transform.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="With --upload-bq: read CSVs and print row counts but do not upload.",
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

    if args.upload_bq:
        print("\n========================================")
        print("  Step 3: Upload to BigQuery")
        print("========================================")
        try:
            from scripts.upload_to_bq import main as bq_main
            import sys as _sys

            # Inject --dry-run flag into argv for upload_to_bq.main() if requested
            _argv_backup = _sys.argv
            _sys.argv = ["upload_to_bq"]
            if args.dry_run:
                _sys.argv.append("--dry-run")
            try:
                bq_main()
            finally:
                _sys.argv = _argv_backup
        except Exception as e:
            print(f"\n[FAIL] BigQuery upload failed: {e}")
            raise

    elapsed = time.time() - t0
    print(f"\n✓ Pipeline complete in {elapsed:.1f}s")
    print("  → Open data/clean/dashboard_data.xlsx in Excel")
    print("  → Connect Tableau to malaysia_project.db")
    if args.upload_bq and not args.dry_run:
        print("  → BigQuery tables updated in GCP")


if __name__ == "__main__":
    main()
