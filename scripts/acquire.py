"""
acquire.py
==========
Download raw datasets from OpenDOSM, MoH Malaysia GitHub, and the World Bank API.

Usage:
    python -m scripts.acquire            # download all (skip existing files)
    python -m scripts.acquire --force    # re-download even if files exist
"""

import argparse
import time
from io import StringIO

import pandas as pd
import requests

from scripts.config import (
    DOSM_API,
    DOSM_CPI_ANNUAL_CSV,
    DOSM_INEQUALITY_CSV,
    DOSM_POPULATION_CSV,
    MOH_BASE,
    RAW,
    WB_BASE,
    WB_INDICATORS,
)

TIMEOUT = 30  # seconds per request


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


def fetch_json(url: str, params: dict | None = None, retries: int = 3) -> list | dict:
    """GET JSON with timeout and up to `retries` retries on transient failures."""
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"HTTP error fetching {url}: {e}") from e
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt == retries:
                raise RuntimeError(
                    f"Failed to fetch {url} after {retries} attempts: {e}"
                ) from e
            wait = 2**attempt
            print(f"  Attempt {attempt} failed ({e}); retrying in {wait}s…")
            time.sleep(wait)


def fetch_csv(url: str, retries: int = 3) -> pd.DataFrame:
    """Download a CSV with timeout and up to `retries` retries."""
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
            return pd.read_csv(StringIO(resp.text))
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"HTTP error fetching {url}: {e}") from e
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt == retries:
                raise RuntimeError(
                    f"Failed to fetch {url} after {retries} attempts: {e}"
                ) from e
            wait = 2**attempt
            print(f"  Attempt {attempt} failed ({e}); retrying in {wait}s…")
            time.sleep(wait)


# ---------------------------------------------------------------------------
# Source-specific downloaders
# ---------------------------------------------------------------------------


def acquire_dosm(force: bool = False) -> None:
    """Download OpenDOSM household income, poverty, and population datasets."""
    datasets = [
        ("hh_income_parlimen", {"id": "hh_income_parlimen", "limit": 2000}),
        ("hh_poverty_parlimen", {"id": "hh_poverty_parlimen", "limit": 2000}),
        ("hh_income_state", {"id": "hh_income_state", "limit": 2000}),
        ("hh_poverty_state", {"id": "hh_poverty_state", "limit": 2000}),
    ]

    for name, params in datasets:
        dest = RAW / f"{name}.csv"
        if dest.exists() and not force:
            print(f"  [skip] {name}.csv already exists")
            continue
        df = pd.DataFrame(fetch_json(DOSM_API, params=params))
        df.to_csv(dest, index=False)
        print(f"  [ok]   {name}.csv: {len(df)} rows")

    # Population: API filter is broken; use direct CSV download
    dest = RAW / "population_state.csv"
    if dest.exists() and not force:
        print(f"  [skip] population_state.csv already exists")
    else:
        df = fetch_csv(DOSM_POPULATION_CSV)
        df.to_csv(dest, index=False)
        print(f"  [ok]   population_state.csv: {len(df)} rows")

    # Inequality (official state-level Gini): direct CSV more reliable than API
    dest = RAW / "hh_inequality_state.csv"
    if dest.exists() and not force:
        print(f"  [skip] hh_inequality_state.csv already exists")
    else:
        df = fetch_csv(DOSM_INEQUALITY_CSV)
        df.to_csv(dest, index=False)
        print(f"  [ok]   hh_inequality_state.csv: {len(df)} rows")

    # National CPI: annual index by division (2-digit MCOICOP), 1960–present
    dest = RAW / "cpi_national.csv"
    if dest.exists() and not force:
        print(f"  [skip] cpi_national.csv already exists")
    else:
        df = fetch_csv(DOSM_CPI_ANNUAL_CSV)
        df.to_csv(dest, index=False)
        print(f"  [ok]   cpi_national.csv: {len(df)} rows")


def acquire_moh(force: bool = False) -> None:
    """Download MoH Malaysia public facility and bed utilisation data."""
    files = {
        "moh_facilities.csv": f"{MOH_BASE}/facilities_master.csv",
        "moh_beds.csv": f"{MOH_BASE}/bedutil_facility.csv",
    }

    for name, url in files.items():
        dest = RAW / name
        if dest.exists() and not force:
            print(f"  [skip] {name} already exists")
            continue
        df = fetch_csv(url)
        df.to_csv(dest, index=False)
        print(f"  [ok]   {name}: {len(df)} rows")


def acquire_worldbank(force: bool = False) -> None:
    """Download World Bank national-level health indicators for Malaysia."""
    dest = RAW / "worldbank_malaysia.csv"
    if dest.exists() and not force:
        print("  [skip] worldbank_malaysia.csv already exists")
        return

    params = {"format": "json", "per_page": 100, "mrv": 20}
    frames = []
    for code, col in WB_INDICATORS.items():
        data = fetch_json(f"{WB_BASE}/{code}", params=params)
        rows = [
            {"year": int(r["date"]), col: r["value"]}
            for r in (data[1] or [])
            if r["value"] is not None
        ]
        frames.append(pd.DataFrame(rows).set_index("year"))

    wb_df = pd.concat(frames, axis=1).reset_index().sort_values("year")
    wb_df.to_csv(dest, index=False)
    print(f"  [ok]   worldbank_malaysia.csv: {len(wb_df)} rows")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run(force: bool = False) -> None:
    """Download all raw datasets. Skips existing files unless force=True."""
    RAW.mkdir(parents=True, exist_ok=True)

    print("\n--- OpenDOSM ---")
    acquire_dosm(force=force)

    print("\n--- MoH Malaysia ---")
    acquire_moh(force=force)

    print("\n--- World Bank ---")
    acquire_worldbank(force=force)

    print(f"\n✓ Raw data in {RAW}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download raw datasets.")
    parser.add_argument(
        "--force", action="store_true", help="Re-download existing files."
    )
    args = parser.parse_args()
    run(force=args.force)
