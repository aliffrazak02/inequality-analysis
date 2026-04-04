"""
COSC 301 Project — Data Acquisition Script
Malaysia State-Level Socioeconomic & Health Outcomes
=====================================================
Run this script to get data
"""

import requests
import pandas as pd
import json
import os
import time
from datetime import datetime
from pathlib import Path

# ── Directory setup ──────────────────────────────────────────────────────────
# Get project root (parent of scripts folder)
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
LOG_DIR = PROJECT_ROOT / "data" / "logs"
RAW_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = LOG_DIR / "acquisition_log.txt"
log_lines = []


def log(msg, status=None):
    prefix = f"[{status}] " if status else "      "
    line = f"{prefix}{msg}"
    print(line)
    log_lines.append(line)


def save_log():
    with open(LOG_PATH, "w") as f:
        f.write(f"Acquisition run: {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n")
        f.write("\n".join(log_lines))
    print(f"\nLog saved to {LOG_PATH}")


# ── Helper: fetch with retry ──────────────────────────────────────────────────
def fetch_json(url, params=None, retries=3, delay=2):
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise e


def fetch_csv_url(url, save_path, retries=3, delay=2):
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(r.content)
            return True
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise e


# SOURCE 1 — OpenDOSM API  (api.data.gov.my)
# License: Creative Commons Attribution (CC-BY)
# Docs:    https://open.dosm.gov.my/api-docs

BASE_DOSM = "https://api.data.gov.my/data-catalogue"

DOSM_DATASETS = [
    {
        "id": "hh_income_parlimen",
        "desc": "Household income by parliament constituency (up to 2024) — aggregate to state in clean_data.py",
        "save_as": "hh_income_parlimen.csv",
        "limit": 2000,
    },
    {
        "id": "hh_poverty_parlimen",
        "desc": "Household poverty by parliament constituency (up to 2024) — aggregate to state in clean_data.py",
        "save_as": "hh_poverty_parlimen.csv",
        "limit": 2000,
    },
    {
        "id": "population_state",
        "desc": "Population by state (for per-capita normalisation)",
        "save_as": "population_state.csv",
        "limit": 10000,
        "filter": "age@overall_age,sex@overall_sex,ethnicity@overall_ethnicity",
    },
]

log("")
log("SOURCE 1 — OpenDOSM (api.data.gov.my)")
log("-" * 50)

dosm_meta = {}

for ds in DOSM_DATASETS:
    save_path = RAW_DIR / ds["save_as"]
    try:
        params = {"id": ds["id"], "limit": ds["limit"]}
        if "filter" in ds:
            params["filter"] = ds["filter"]
        data = fetch_json(BASE_DOSM, params=params)

        if not data:
            log(f"{ds['id']}: returned empty response", "WARN")
            continue

        df = pd.DataFrame(data)
        df.to_csv(save_path, index=False)

        date_col = (
            "year"
            if "year" in df.columns
            else ("date" if "date" in df.columns else None)
        )
        dosm_meta[ds["id"]] = {
            "rows": len(df),
            "columns": list(df.columns),
            "years": sorted(df[date_col].unique().tolist()) if date_col else "n/a",
            "states": sorted(df["state"].unique().tolist())
            if "state" in df.columns
            else "n/a",
        }

        log(f"PASS  {ds['id']}: {len(df)} rows, cols={list(df.columns)}", "OK")
        log(f"      years: {dosm_meta[ds['id']]['years']}")
        log(
            f"      states ({len(dosm_meta[ds['id']]['states'])}): {dosm_meta[ds['id']]['states']}"
        )

    except Exception as e:
        log(f"FAIL  {ds['id']}: {e}", "FAIL")

meta_path = RAW_DIR / "dosm_metadata.json"
with open(meta_path, "w") as f:
    json.dump(dosm_meta, f, indent=2)
log(f"Metadata saved: {meta_path}")


# SOURCE 2 — MoH Malaysia Open Data  (data.moh.gov.my)
# License: Malaysian Open Data License (free for research)
# Docs:    https://github.com/MoH-Malaysia
# Note:    MoH publishes data directly on GitHub as CSVs — more reliable
#          than scraping the portal. We pull from the official MoH GitHub.

MOH_BASE = "https://raw.githubusercontent.com/MoH-Malaysia/data-resources-public/main"

MOH_DATASETS = [
    {
        "path": "facilities_master.csv",
        "desc": "Public hospitals and health clinics by state (combined)",
        "save_as": "moh_facilities.csv",
    },
    {
        "path": "bedutil_facility.csv",
        "desc": "Hospital bed counts and utilisation by facility",
        "save_as": "moh_beds.csv",
    },
]

log("")
log("SOURCE 2 — MoH Malaysia GitHub (github.com/MoH-Malaysia)")
log("-" * 50)

for ds in MOH_DATASETS:
    save_path = RAW_DIR / ds["save_as"]
    url = f"{MOH_BASE}/{ds['path']}"
    try:
        fetch_csv_url(url, save_path)
        df = pd.read_csv(save_path)
        log(f"PASS  {ds['save_as']}: {len(df)} rows, cols={list(df.columns)}", "OK")
        if "state" in df.columns:
            log(f"      states: {sorted(df['state'].unique().tolist())}")
        if "year" in df.columns:
            log(f"      years: {sorted(df['year'].unique().tolist())}")
    except Exception as e:
        log(f"FAIL  {ds['save_as']}: {e}", "FAIL")
        log(f"      URL attempted: {url}")
        log(
            "      FALLBACK: download manually from https://github.com/MoH-Malaysia/data-resources-public"
        )


# SOURCE 3 — World Bank API (backup / cross-validation)
# For Malaysia (iso: MYS) health + macro indicators
# License: CC-BY 4.0
WB_BASE = "https://api.worldbank.org/v2/country/MYS/indicator"

WB_INDICATORS = [
    ("SP.DYN.LE00.IN", "life_expectancy", "Life expectancy at birth"),
    (
        "SP.DYN.IMRT.IN",
        "infant_mortality",
        "Infant mortality rate (per 1000 live births)",
    ),
    ("SH.XPD.CHEX.GD.ZS", "health_exp_gdp", "Current health expenditure (% of GDP)"),
    ("SH.MED.BEDS.ZS", "hospital_beds", "Hospital beds (per 1,000 people)"),
]

log("")
log("SOURCE 3 — World Bank API (api.worldbank.org) — national level backup")
log("-" * 50)

wb_frames = []
for indicator_code, col_name, desc in WB_INDICATORS:
    url = f"{WB_BASE}/{indicator_code}"
    try:
        params = {"format": "json", "per_page": 100, "mrv": 20}
        data = fetch_json(url, params=params)
        records = data[1] if isinstance(data, list) and len(data) > 1 else []
        rows = [
            {"year": int(r["date"]), col_name: r["value"]}
            for r in records
            if r["value"] is not None
        ]
        if rows:
            wb_frames.append(pd.DataFrame(rows).set_index("year"))
            log(f"PASS  {col_name}: {len(rows)} year-records", "OK")
        else:
            log(f"WARN  {col_name}: no data returned", "WARN")
    except Exception as e:
        log(f"FAIL  {col_name} ({indicator_code}): {e}", "FAIL")

if wb_frames:
    wb_df = pd.concat(wb_frames, axis=1).reset_index().sort_values("year")
    wb_path = RAW_DIR / "worldbank_malaysia.csv"
    wb_df.to_csv(wb_path, index=False)
    log(f"World Bank combined: {len(wb_df)} rows saved to {wb_path}")

# VALIDATION SUMMARY
# Checks state name consistency across sources (critical for joining)

log("")
log("VALIDATION — State name consistency check")
log("-" * 50)

# Official 16 state/territory codes used by DOSM
OFFICIAL_STATES = [
    "Johor",
    "Kedah",
    "Kelantan",
    "Melaka",
    "Negeri Sembilan",
    "Pahang",
    "Perak",
    "Perlis",
    "Pulau Pinang",
    "Sabah",
    "Sarawak",
    "Selangor",
    "Terengganu",
    "W.P. Kuala Lumpur",
    "W.P. Labuan",
    "W.P. Putrajaya",
]

SOURCE_FILES = {
    "hh_income_parlimen": RAW_DIR / "hh_income_parlimen.csv",
    "hh_poverty_parlimen": RAW_DIR / "hh_poverty_parlimen.csv",
    "moh_facilities": RAW_DIR / "moh_facilities.csv",
    "moh_beds": RAW_DIR / "moh_beds.csv",
}

for name, path in SOURCE_FILES.items():
    if not os.path.exists(path):
        log(f"SKIP  {name}: file not found", "SKIP")
        continue
    try:
        df = pd.read_csv(path)
        if "state" not in df.columns:
            log(f"SKIP  {name}: no 'state' column", "SKIP")
            continue
        found = set(df["state"].unique())
        mismatches = found - set(OFFICIAL_STATES)
        missing = set(OFFICIAL_STATES) - found
        if not mismatches and not missing:
            log(f"PASS  {name}: all 16 states match", "OK")
        else:
            if mismatches:
                log(f"WARN  {name}: unexpected state names: {mismatches}", "WARN")
                log("      FIX: add to STATE_NAME_MAP in clean_data.py")
            if missing:
                log(f"WARN  {name}: missing states: {missing}", "WARN")
    except Exception as e:
        log(f"FAIL  {name} validation: {e}", "FAIL")

# FINAL SUMMARY

log("")
log("=" * 50)
log("FILES IN data/raw/:")
for f in sorted(os.listdir(str(RAW_DIR))):
    fpath = RAW_DIR / f
    size_kb = fpath.stat().st_size / 1024
    log(f"  {f:<40} {size_kb:>7.1f} KB")

log("")
log("NEXT STEPS:")
log("  1. Review any FAIL/WARN lines above")
log("  2. For FAIL items, use manual download links in comments")
log("  3. Run clean_data.py to standardise state names and merge")
log("  4. If all sources pass -> you're clear to finalise proposal")

save_log()
print("\nDone. Check data/logs/acquisition_log.txt for full report.")
