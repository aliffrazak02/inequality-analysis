# Caveats and Limitations

**COSC 301 Project — Malaysia State-Level Socioeconomic & Health Outcomes**

---

## 1. MOH Health Data is a Point-in-Time Snapshot (No Year Dimension)

**What the problem is:** `moh_facilities.csv` and `moh_beds.csv` contain no year or date column. Based on the source repository's commit history, the data reflects the state of health infrastructure as of approximately **late 2023 or 2024**.

**How the pipeline handles it:** The ETL notebook (`03_transform.ipynb`) cross-joins the snapshot against all three analysis years (2019, 2022, 2024), making the health infrastructure values **identical across all years** in `health_state.csv`.

**Impact on each research question:**

| Question | Impact |
|---|---|
| Q1 — Income & poverty | None — uses only socioeconomic data |
| Q2 — Health infrastructure rankings | Low — rankings are valid; the data represents ~2024 infrastructure |
| Q3 — Inequality ↔ health correlation | Moderate — correlating 2022 income with ~2024 health infrastructure introduces a ~2-year temporal mismatch. Infrastructure changes slowly (new hospitals take years to build), so the mismatch is unlikely to materially change conclusions, but it should be disclosed |
| Q4 — Trends over time | None — trend analysis uses only the `socioeconomic_state` table |
| Q5 — Long-term trends | None — uses `historical_state`, a separate DOSM table |

**Mitigation:** Health data is used only as a cross-sectional baseline. Temporal trend analysis of health outcomes is explicitly out of scope.

---

## 2. Population Data is from the 2020 Census Only

**What the problem is:** `population_state.csv` contains a single snapshot from the 2020 Population and Housing Census. There is no data for 2019 or 2024.

**Impact:** Per-capita health metrics (`beds_per_1000`, `facilities_per_100k`) use 2020 population as a proxy for all analysis years. Malaysia's population grew at approximately 1–2% per year in this period, so:
- 2019 per-capita values are slightly *understated* (denominator is too large)
- 2024 per-capita values are slightly *overstated* (denominator is too small)

**Magnitude:** With ~1.5% annual growth over 4 years, the 2024 population is roughly 6% larger than 2020. This means `beds_per_1000` for 2024 is overstated by ~6% on average — a small but non-trivial error.

**Mitigation:** Health analysis is conducted on the 2022 reference slice only. The 2020 population is a reasonable approximation for 2022 (±2 years).

---

## 3. Gini Measures Inter-Constituency Dispersion, Not Household-Level Inequality

**What the problem is:** The `gini` column in `socioeconomic_state.csv` is computed from constituency-level mean income values within each state, not from individual household income data. It captures how unevenly income means are distributed across the state's parliamentary constituencies.

**Impact:** This is an *ecological* measure of geographic income dispersion, not a standard household Gini coefficient (which would require microdata). The two are correlated but not equivalent. Results should not be compared to published DOSM state-level Gini figures, which are household-level.

**Mitigation:** The variable is labelled `gini` throughout but interpreted as *inter-constituency income inequality* in all analysis outputs.

---

## 4. Constituency-Level Aggregation Uses Unweighted Means

**What the problem is:** State-level `income_mean` and `poverty_absolute` are computed as simple (unweighted) means across all parliamentary constituencies. Constituencies differ substantially in population size — a small rural constituency receives the same weight as a large urban one.

**Impact:** States with many small low-income rural constituencies may have slightly lower (more conservative) income estimates than a population-weighted approach would produce. Conversely, poverty rates in states where poverty is concentrated in a few large constituencies may be understated.

**Mitigation:** DOSM does not publish constituency-level population weights alongside the income data, so population-weighting is not feasible with the available data. This limitation is noted; findings at the state level remain directionally valid.

---

## 5. 2024 Socioeconomic Data is Provisional

**What the problem is:** DOSM labels the 2024 Household Income Survey data as provisional. Figures may be revised in subsequent releases.

**Impact:** The Q4 trend analysis (2019 → 2024) uses provisional endpoints. Income growth and poverty reduction figures for 2024 should be treated as indicative, not definitive.

**Mitigation:** Cross-sectional rankings (Q1) use 2022 as the reference year, which is the most complete and finalised survey wave.

---

## 6. Small Sample Size for Correlation Analysis

**What the problem is:** With only 16 states, all correlation and regression analyses (Q3) have very low statistical power. A Pearson or Spearman correlation with n = 16 requires |r| ≥ 0.50 to reach significance at α = 0.05 (two-tailed).

**Impact:** Failure to find a statistically significant correlation does not imply no relationship. Conversely, any significant result should be interpreted cautiously as it could be driven by a single influential state (e.g., W.P. Kuala Lumpur or W.P. Labuan, which are outliers in both income and geography).

**Mitigation:** Both Pearson and Spearman correlations are reported. OLS results are presented as exploratory only, with R² and p-values clearly labelled.

---

## 7. 2020 and 2021 Missing from Socioeconomic Data

**What the problem is:** No DOSM Household Income and Expenditure Survey (HIES) was conducted in 2020 or 2021. Survey fieldwork was suspended during the COVID-19 pandemic.

**Impact:** The `socioeconomic_state` table has three survey waves — 2019, 2022, and 2024 — with a 3-year gap that spans the pandemic period. Trend analysis cannot capture the income shock or recovery at the state level for those years.

**Mitigation:** The `historical_state` table (DOSM state-level aggregates, 1970–2022) confirms the same gap: the most recent pre-pandemic survey is 2019 and the next is 2022. All trend charts annotate this gap explicitly.

---

## 8. Historical State Data vs Constituency-Derived Data

**What the problem is:** The project contains two sources of state-level socioeconomic data that are *not directly comparable*:

| Table | Source | Aggregation | Income figures |
|---|---|---|---|
| `socioeconomic_state` | Constituency-level HIES | Unweighted mean of constituency means | Derived; not DOSM's published state totals |
| `historical_state` | Official DOSM state tables | Population-weighted (DOSM methodology) | Official published figures |

**Impact:** Income values for overlapping years (2019, 2022) will differ between the two tables because of different aggregation methods. `historical_state` figures are the authoritative ones for comparison with other publications.

**Mitigation:** The two tables serve different purposes. `socioeconomic_state` is used for Q1–Q4 (cross-sectional analysis and 2019–2024 trends). `historical_state` is used exclusively for Q5 (long-term 1970–2022 trends). They are never directly combined in the analysis.

---

## 9. Federal Territories as Statistical Units

W.P. Kuala Lumpur, W.P. Putrajaya, and W.P. Labuan are Federal Territories, not states. Each has a distinct demographic profile that makes direct comparison with general-purpose states problematic.

The analysis handles each territory differently:

| Territory | Classification | Treatment |
|---|---|---|
| **W.P. Kuala Lumpur** | `capital` | **Retained** — economically significant urban capital; included in all charts but visually distinguished with `*` and a distinct colour. Included in OLS regression (so its influence is transparent) but readers are explicitly warned it is an urban outlier. |
| **W.P. Putrajaya** | `admin` | **Excluded** from main analysis (`df_main`) — it is an artificial administrative enclave purpose-built for government workers (~90 000 residents). Its income and health metrics reflect a non-representative government-servant population, not a general state. It remains available in `df` for full-data sensitivity checks. |
| **W.P. Labuan** | `island_ft` | **Retained and classified as East Malaysia** — geographically in Borneo, economically linked to Sabah/Sarawak. Already included in the East Malaysia group (`EAST = {"Sabah", "Sarawak", "W.P. Labuan"}`). |

A `territory_type` column is now included in all clean tables (`state`, `capital`, `admin`, `island_ft`) to support further sensitivity analysis.
