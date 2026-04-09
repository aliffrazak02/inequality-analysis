"""
transform.py
============
ETL pipeline: clean raw data, build analysis tables, compute SDI scores,
and export to CSV, SQLite, and Excel (for Tableau / Excel dashboards).

Usage:
    python -m scripts.transform
"""

import sqlite3

import numpy as np
import pandas as pd

from scripts.config import (
    ANALYSIS_YEARS,
    CLEAN,
    CPI_STATE_COLS,
    DB_PATH,
    FT_TYPES,
    OUT_XLSX,
    OVERLAP_YEARS,
    RAW,
    SDI_REF_YEAR,
    SDI_WEIGHTS,
    STATE_CODES,
    STATE_NORM,
)


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


def normalise_state(series: pd.Series) -> pd.Series:
    """Normalise state name variants to their canonical form."""
    return series.str.strip().replace(STATE_NORM)


def gini_coefficient(series: pd.Series) -> float:
    """Gini coefficient of a 1-D array (population mean-based formula)."""
    arr = np.sort(series.dropna().values)
    n = len(arr)
    if n == 0 or arr.sum() == 0:
        return np.nan
    return (2 * np.dot(np.arange(1, n + 1), arr) / (n * arr.sum())) - (n + 1) / n


def minmax(s: pd.Series) -> pd.Series:
    """Min-max normalise a series to [0, 1]."""
    return (s - s.min()) / (s.max() - s.min())


# ---------------------------------------------------------------------------
# Build functions
# ---------------------------------------------------------------------------


def build_socioeconomic() -> pd.DataFrame:
    """
    Aggregate parliament-constituency income and poverty data to state level.
    Returns state × year data for OVERLAP_YEARS with income, poverty, and Gini.
    """
    income_raw = pd.read_csv(RAW / "hh_income_parlimen.csv")
    poverty_raw = pd.read_csv(RAW / "hh_poverty_parlimen.csv")

    for df in [income_raw, poverty_raw]:
        df["state"] = normalise_state(df["state"])
        df["year"] = pd.to_datetime(df["date"]).dt.year

    income_state = (
        income_raw.groupby(["state", "year"])
        .agg(
            income_mean=("income_mean", "mean"),
            income_median=("income_median", "mean"),
            gini=("income_mean", gini_coefficient),
            parlimen_count=("parlimen", "count"),
        )
        .reset_index()
    )

    poverty_state = (
        poverty_raw.groupby(["state", "year"])
        .agg(poverty_absolute=("poverty_absolute", "mean"))
        .reset_index()
    )

    socioeconomic = income_state.merge(poverty_state, on=["state", "year"])
    socioeconomic["state_code"] = socioeconomic["state"].map(STATE_CODES)
    socioeconomic["territory_type"] = (
        socioeconomic["state"].map(FT_TYPES).fillna("state")
    )

    return socioeconomic[
        [
            "state_code",
            "state",
            "year",
            "territory_type",
            "income_mean",
            "income_median",
            "poverty_absolute",
            "gini",
            "parlimen_count",
        ]
    ]


def build_population() -> pd.DataFrame:
    """
    Extract overall population totals per (state, year) from population_state.csv.
    Values in the source are in thousands; this function converts to actual counts.
    """
    population_raw = pd.read_csv(RAW / "population_state.csv")
    population_raw["state"] = normalise_state(population_raw["state"])

    pop = population_raw[
        (population_raw["age"] == "overall")
        & (population_raw["sex"] == "both")
        & (population_raw["ethnicity"] == "overall")
    ].copy()

    pop["year"] = pd.to_datetime(pop["date"]).dt.year
    pop["population"] = pop["population"] * 1_000
    return pop[pop["year"].isin(ANALYSIS_YEARS)][["state", "year", "population"]]


def build_health(pop: pd.DataFrame) -> pd.DataFrame:
    """
    Build state × year health infrastructure table with per-capita metrics.
    Infrastructure counts are a static snapshot — the cross-join with years
    makes this joinable with the socioeconomic table; only population denominators differ.
    """
    facilities_raw = pd.read_csv(RAW / "moh_facilities.csv")
    beds_raw = pd.read_csv(RAW / "moh_beds.csv")

    for df in [facilities_raw, beds_raw]:
        df["state"] = normalise_state(df["state"])

    hospital_count = (
        facilities_raw[facilities_raw["type"] == "hospital"]
        .groupby("state")
        .size()
        .rename("hospital_count")
        .reset_index()
    )

    facility_count = (
        facilities_raw.groupby("state").size().rename("facility_count").reset_index()
    )

    # Clamp negative bed counts (known data entry error in source)
    beds_raw["beds_nonicu"] = beds_raw["beds_nonicu"].clip(lower=0)
    beds_raw["beds_icu"] = beds_raw["beds_icu"].clip(lower=0)

    beds_state = (
        beds_raw.groupby("state")
        .agg(beds_nonicu=("beds_nonicu", "sum"), beds_icu=("beds_icu", "sum"))
        .reset_index()
    )
    beds_state["beds_total"] = beds_state["beds_nonicu"] + beds_state["beds_icu"]

    states = sorted(pop["state"].dropna().unique())
    years = sorted(pop["year"].dropna().unique())
    base = pd.DataFrame(
        [(s, y) for s in states for y in years],
        columns=["state", "year"],
    )

    health = (
        base.merge(pop, on=["state", "year"], how="left")
        .merge(hospital_count, on="state", how="left")
        .merge(facility_count, on="state", how="left")
        .merge(beds_state, on="state", how="left")
    )

    health["beds_per_1000"] = health["beds_total"] / (health["population"] / 1_000)
    health["facilities_per_100k"] = health["facility_count"] / (
        health["population"] / 100_000
    )
    health["state_code"] = health["state"].map(STATE_CODES)
    health["territory_type"] = health["state"].map(FT_TYPES).fillna("state")

    return health[
        [
            "state_code",
            "state",
            "year",
            "territory_type",
            "population",
            "hospital_count",
            "facility_count",
            "beds_nonicu",
            "beds_icu",
            "beds_total",
            "beds_per_1000",
            "facilities_per_100k",
        ]
    ]


def build_combined(socio: pd.DataFrame) -> pd.DataFrame:
    """
    Merge historical state-level data (1970–2022) with recent parliament-derived data
    (2019, 2022, 2024). DOSM's official state-level Gini is applied where available,
    overriding the inter-constituency proxy for 2019 and 2022.
    """
    income_hist = pd.read_csv(RAW / "hh_income_state.csv")
    poverty_hist = pd.read_csv(RAW / "hh_poverty_state.csv")

    for df in [income_hist, poverty_hist]:
        df["state"] = normalise_state(df["state"])
        df["year"] = pd.to_datetime(df["date"]).dt.year

    historical = income_hist[["state", "year", "income_mean", "income_median"]].merge(
        poverty_hist[
            [
                "state",
                "year",
                "poverty_absolute",
                "poverty_hardcore",
                "poverty_relative",
            ]
        ],
        on=["state", "year"],
        how="left",
    )
    historical["state_code"] = historical["state"].map(STATE_CODES)
    historical["territory_type"] = historical["state"].map(FT_TYPES).fillna("state")

    # Trim overlap years from historical; drop columns absent from parliament data
    hist_trimmed = (
        historical[~historical["year"].isin(OVERLAP_YEARS)]
        .drop(columns=["poverty_hardcore", "poverty_relative"])
        .assign(gini=np.nan)
    )

    socio_trimmed = socio.drop(columns=["parlimen_count"])

    combined = (
        pd.concat([hist_trimmed, socio_trimmed], ignore_index=True)
        .sort_values(["state", "year"])
        .reset_index(drop=True)
    )[
        [
            "state_code",
            "state",
            "year",
            "territory_type",
            "income_mean",
            "income_median",
            "poverty_absolute",
            "gini",
        ]
    ]

    # Apply DOSM official state-level Gini where available (hh_inequality_state.csv is optional)
    gini_path = RAW / "hh_inequality_state.csv"
    if gini_path.exists():
        gini_state_raw = pd.read_csv(gini_path)
        gini_state_raw["state"] = normalise_state(gini_state_raw["state"])
        gini_state_raw["year"] = pd.to_datetime(gini_state_raw["date"]).dt.year
        gini_lookup = gini_state_raw.set_index(["state", "year"])["gini"]

        dosm_mask = combined.set_index(["state", "year"]).index.isin(gini_lookup.index)
        combined.loc[dosm_mask, "gini"] = combined.loc[dosm_mask].apply(
            lambda r: gini_lookup.get((r["state"], r["year"]), np.nan), axis=1
        )

    return combined


def build_sdi(socio: pd.DataFrame, health: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the Socioeconomic Deprivation Index (SDI) for SDI_REF_YEAR.

    Components (all normalised to [0, 1] where 1 = most deprived):
      - n_poverty    = poverty_absolute (direct)
      - n_gini       = gini (direct)
      - n_income     = 1 - income_median (inverted: lower income → worse)
      - n_beds       = 1 - beds_per_1000 (inverted: fewer beds → worse)
      - n_facilities = 1 - facilities_per_100k (inverted)

    Weighted composite: see SDI_WEIGHTS in config.py
    Also computes sensitivity variants:
      - sdi_rank_no_terr: re-normalised excluding federal territories
      - sdi_score_eq / sdi_rank_eq: equal 20% weights
    """
    econ = socio[socio["year"] == SDI_REF_YEAR].copy()
    h = health[health["year"] == SDI_REF_YEAR].copy()

    df = econ.merge(
        h[["state_code", "beds_per_1000", "facilities_per_100k"]],
        on="state_code",
    )

    # Normalise components
    df["n_poverty"] = minmax(df["poverty_absolute"])
    df["n_gini"] = minmax(df["gini"])
    df["n_income"] = 1 - minmax(df["income_median"])
    df["n_beds"] = 1 - minmax(df["beds_per_1000"])
    df["n_facilities"] = 1 - minmax(df["facilities_per_100k"])

    # Weighted SDI score
    df["sdi_score"] = sum(df[col] * w for col, w in SDI_WEIGHTS.items())
    df["sdi_rank"] = df["sdi_score"].rank(ascending=False).astype(int)

    # Double deprivation flag
    econ_dep = df["n_poverty"] + df["n_gini"] + df["n_income"]
    health_dep = df["n_beds"] + df["n_facilities"]
    df["double_deprivation"] = (econ_dep > econ_dep.median()) & (
        health_dep > health_dep.median()
    )

    # Sensitivity 1: re-normalise excluding federal territories
    territories = ["W.P. Kuala Lumpur", "W.P. Labuan", "W.P. Putrajaya"]
    df_no_terr = df[~df["state"].isin(territories)].copy()
    df_no_terr["n_poverty"] = minmax(df_no_terr["poverty_absolute"])
    df_no_terr["n_gini"] = minmax(df_no_terr["gini"])
    df_no_terr["n_income"] = 1 - minmax(df_no_terr["income_median"])
    df_no_terr["n_beds"] = 1 - minmax(df_no_terr["beds_per_1000"])
    df_no_terr["n_facilities"] = 1 - minmax(df_no_terr["facilities_per_100k"])
    df_no_terr["sdi_score_no_terr"] = sum(
        df_no_terr[col] * w for col, w in SDI_WEIGHTS.items()
    )
    df_no_terr["sdi_rank_no_terr"] = (
        df_no_terr["sdi_score_no_terr"].rank(ascending=False).astype(int)
    )
    df = df.merge(
        df_no_terr[["state_code", "sdi_rank_no_terr"]], on="state_code", how="left"
    )

    # Sensitivity 2: equal weights (20% each)
    eq_weights = {k: 0.20 for k in SDI_WEIGHTS}
    df["sdi_score_eq"] = sum(df[col] * w for col, w in eq_weights.items())
    df["sdi_rank_eq"] = df["sdi_score_eq"].rank(ascending=False).astype(int)

    cols = [
        "state_code",
        "state",
        "territory_type",
        "poverty_absolute",
        "gini",
        "income_median",
        "beds_per_1000",
        "facilities_per_100k",
        "n_poverty",
        "n_gini",
        "n_income",
        "n_beds",
        "n_facilities",
        "sdi_score",
        "sdi_rank",
        "double_deprivation",
        "sdi_rank_no_terr",
        "sdi_score_eq",
        "sdi_rank_eq",
    ]
    return df[cols].sort_values("sdi_rank").reset_index(drop=True)


def build_cpi() -> pd.DataFrame:
    """
    Build state × year annual CPI table from monthly cpi_state.csv.

    Source file is wide-format: columns are date, category, then one column
    per state (slugified names). Filters to 'overall' category and averages
    monthly values to produce an annual index (base year 2010 = 100).

    Returns long-format table: state_code, state, year, cpi_overall.
    """
    cpi_raw = pd.read_csv(RAW / "cpi_state.csv")

    cpi_overall = cpi_raw[cpi_raw["category"] == "overall"].copy()
    cpi_overall["year"] = pd.to_datetime(cpi_overall["date"]).dt.year

    state_cols = [
        c for c in cpi_overall.columns if c not in ("date", "category", "year")
    ]
    cpi_long = cpi_overall.melt(
        id_vars=["year"],
        value_vars=state_cols,
        var_name="state_slug",
        value_name="cpi_overall",
    )

    cpi_annual = (
        cpi_long.groupby(["state_slug", "year"])["cpi_overall"].mean().reset_index()
    )

    cpi_annual["state"] = cpi_annual["state_slug"].map(CPI_STATE_COLS)
    cpi_annual["state_code"] = cpi_annual["state"].map(STATE_CODES)

    return (
        cpi_annual[["state_code", "state", "year", "cpi_overall"]]
        .dropna(subset=["state"])
        .sort_values(["state", "year"])
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


def export_excel(
    combined: pd.DataFrame,
    health: pd.DataFrame,
    sdi: pd.DataFrame,
    cpi: pd.DataFrame,
) -> None:
    """Write a four-sheet Excel workbook to OUT_XLSX."""
    with pd.ExcelWriter(OUT_XLSX, engine="openpyxl") as writer:
        sdi.to_excel(writer, sheet_name="sdi_scores", index=False)
        combined.to_excel(writer, sheet_name="combined_state", index=False)
        health.to_excel(writer, sheet_name="health_state", index=False)
        cpi.to_excel(writer, sheet_name="cpi_state", index=False)
    print(
        f"✓ {OUT_XLSX.name}: 4 sheets (sdi_scores, combined_state, health_state, cpi_state)"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run() -> None:
    """Full ETL: load raw data → build tables → save CSV + SQLite + Excel."""
    CLEAN.mkdir(parents=True, exist_ok=True)

    print("\n--- Building socioeconomic table ---")
    socio = build_socioeconomic()
    print(f"  socioeconomic: {socio.shape}")

    print("\n--- Building population table ---")
    pop = build_population()
    print(f"  population: {pop.shape}")

    print("\n--- Building health infrastructure table ---")
    health = build_health(pop)
    print(f"  health: {health.shape}")

    print("\n--- Building combined historical table ---")
    combined = build_combined(socio)
    print(
        f"  combined: {combined.shape}, years {combined.year.min()}–{combined.year.max()}"
    )

    print("\n--- Building CPI table ---")
    cpi = build_cpi()
    print(f"  cpi: {cpi.shape}, years {cpi.year.min()}–{cpi.year.max()}")

    # Attach annual CPI to combined where available
    combined = combined.merge(
        cpi[["state_code", "year", "cpi_overall"]],
        on=["state_code", "year"],
        how="left",
    )

    print("\n--- Computing SDI scores ---")
    sdi = build_sdi(socio, health)
    print(f"  sdi: {sdi.shape}")

    print("\n--- Saving outputs ---")
    combined.to_csv(CLEAN / "combined_state.csv", index=False)
    print(f"  ✓ combined_state.csv")

    health.to_csv(CLEAN / "health_state.csv", index=False)
    print(f"  ✓ health_state.csv")

    sdi.to_csv(CLEAN / "sdi_scores.csv", index=False)
    print(f"  ✓ sdi_scores.csv")

    cpi.to_csv(CLEAN / "cpi_state.csv", index=False)
    print(f"  ✓ cpi_state.csv")

    with sqlite3.connect(DB_PATH) as con:
        combined.to_sql("combined_state", con, if_exists="replace", index=False)
        health.to_sql("health_state", con, if_exists="replace", index=False)
        sdi.to_sql("sdi_scores", con, if_exists="replace", index=False)
        cpi.to_sql("cpi_state", con, if_exists="replace", index=False)
    print(
        f"  ✓ {DB_PATH.name} (tables: combined_state, health_state, sdi_scores, cpi_state)"
    )

    export_excel(combined, health, sdi, cpi)


if __name__ == "__main__":
    run()
