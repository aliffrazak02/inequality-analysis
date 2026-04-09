"""
config.py
=========
Shared constants, paths, and mappings for the ETL pipeline.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"
FIGURES = ROOT / "figures"
DB_PATH = ROOT / "malaysia_project.db"
OUT_XLSX = CLEAN / "dashboard_data.xlsx"

# ---------------------------------------------------------------------------
# State normalisation
# ---------------------------------------------------------------------------
STATE_NORM = {
    "W.P Kuala Lumpur": "W.P. Kuala Lumpur",
    "W.P Labuan": "W.P. Labuan",
    "W.P Putrajaya": "W.P. Putrajaya",
    "WP Kuala Lumpur": "W.P. Kuala Lumpur",
    "WP Labuan": "W.P. Labuan",
    "WP Putrajaya": "W.P. Putrajaya",
}

STATE_CODES = {
    "Johor": "JHR",
    "Kedah": "KDH",
    "Kelantan": "KTN",
    "Melaka": "MLK",
    "Negeri Sembilan": "NSN",
    "Pahang": "PHG",
    "Perak": "PRK",
    "Perlis": "PLS",
    "Pulau Pinang": "PNG",
    "Sabah": "SBH",
    "Sarawak": "SWK",
    "Selangor": "SGR",
    "Terengganu": "TRG",
    "W.P. Kuala Lumpur": "KUL",
    "W.P. Labuan": "LBN",
    "W.P. Putrajaya": "PJY",
}

FT_TYPES = {
    "W.P. Kuala Lumpur": "capital",
    "W.P. Putrajaya": "admin",
    "W.P. Labuan": "island_ft",
}

# ---------------------------------------------------------------------------
# Analysis config
# ---------------------------------------------------------------------------
OVERLAP_YEARS = [2019, 2022]
ANALYSIS_YEARS = [2019, 2022, 2024]
SDI_REF_YEAR = 2022  # Most complete survey year used for SDI computation

SDI_WEIGHTS = {
    "n_poverty": 0.25,
    "n_gini": 0.20,
    "n_income": 0.25,
    "n_beds": 0.15,
    "n_facilities": 0.15,
}

# ---------------------------------------------------------------------------
# API URLs
# ---------------------------------------------------------------------------
DOSM_API = "https://api.data.gov.my/data-catalogue"
DOSM_POPULATION_CSV = "https://storage.dosm.gov.my/population/population_state.csv"
DOSM_INEQUALITY_CSV = "https://storage.dosm.gov.my/hies/hh_inequality_state.csv"
DOSM_CPI_STATE_CSV = "https://storage.dosm.gov.my/cpi/cpi_state.csv"
MOH_BASE = "https://raw.githubusercontent.com/MoH-Malaysia/data-resources-public/main"
WB_BASE = "https://api.worldbank.org/v2/country/MYS/indicator"

# CPI state CSV uses slugified column names — map to canonical state names
CPI_STATE_COLS = {
    "johor": "Johor",
    "kedah": "Kedah",
    "kelantan": "Kelantan",
    "melaka": "Melaka",
    "negeri_sembilan": "Negeri Sembilan",
    "pahang": "Pahang",
    "perak": "Perak",
    "perlis": "Perlis",
    "pulau_pinang": "Pulau Pinang",
    "sabah": "Sabah",
    "sarawak": "Sarawak",
    "selangor": "Selangor",
    "terengganu": "Terengganu",
    "wp-kuala-lumpur": "W.P. Kuala Lumpur",
    "wp-labuan": "W.P. Labuan",
    "wp-putrajaya": "W.P. Putrajaya",
}

WB_INDICATORS = {
    "SP.DYN.LE00.IN": "life_expectancy",
    "SP.DYN.IMRT.IN": "infant_mortality",
    "SH.XPD.CHEX.GD.ZS": "health_exp_gdp",
    "SH.MED.BEDS.ZS": "hospital_beds",
}
