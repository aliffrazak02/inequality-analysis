# Methodology

**COSC 301 Project — Malaysia State-Level Socioeconomic & Health Outcomes**

---

## Research Questions

1. **Income & poverty landscape** — Which states are richest and most deprived?
2. **Health infrastructure** — Which states are best and worst served per capita?
3. **Inequality ↔ health correlation** — Does income inequality predict poorer health infrastructure?
4. **Trends over time** — How did income and poverty change between 2019 and 2024?

---

## Unit of Analysis

The primary unit of analysis is the **Malaysian state**, of which there are 16 (13 states + 3 Federal Territories). All raw data collected at finer granularity (parliamentary constituency, hospital) is aggregated up to this level before analysis.

---

## Data Pipeline

The project follows a three-stage pipeline:

```
data/raw/          →  notebook/03_transform.ipynb  →  data/clean/
(source files)         (ETL)                           (analysis-ready tables)
```

| Notebook | Purpose |
|---|---|
| `01_acquisition.ipynb` | Downloads and caches raw files; logs acquisition metadata |
| `02_explore.ipynb` | Schema review, missing-value profiling, join-readiness checks |
| `03_transform.ipynb` | Cleans, aggregates, and writes two analytical tables |
| `04_analysis.ipynb` | Answers four research questions; produces statistics |
| `05_visualisation.ipynb` | Generates charts from the clean tables |

---

## Socioeconomic Table Construction

**Sources:** `hh_income_parlimen.csv`, `hh_poverty_parlimen.csv` (DOSM)

**Grain of raw data:** parliamentary constituency × survey year (2019, 2022, 2024)

**Aggregation to state level:**

| Output column | Aggregation rule |
|---|---|
| `income_mean` | Unweighted mean of constituency means within the state |
| `income_median` | Unweighted mean of constituency medians within the state |
| `poverty_absolute` | Unweighted mean of constituency poverty rates within the state |
| `gini` | Gini coefficient computed over constituency-level `income_mean` values — measures *inter-constituency* income dispersion, not household-level inequality |

**Gini formula used:**

$$G = \frac{2 \sum_{i=1}^{n} i \cdot x_i}{n \sum_{i=1}^{n} x_i} - \frac{n+1}{n}$$

where $x_i$ are sorted constituency income means.

---

## Health Infrastructure Table Construction

**Sources:** `moh_facilities.csv`, `moh_beds.csv` (MOH), `population_state.csv` (DOSM 2020 Census)

**Grain of raw data:** individual hospital/facility (no year dimension)

**Aggregation to state level:**

| Output column | Derivation |
|---|---|
| `hospital_count` | Count of facilities where `type == "hospital"` |
| `facility_count` | Count of all facility records |
| `beds_nonicu` | Sum of non-ICU beds across all hospitals in the state |
| `beds_icu` | Sum of ICU beds across all hospitals in the state |
| `beds_total` | `beds_nonicu + beds_icu` |
| `beds_per_1000` | `beds_total / (population / 1 000)` |
| `facilities_per_100k` | `facility_count / (population / 100 000)` |

Because MOH data has no year column, the same infrastructure counts are replicated across all three analysis years (2019, 2022, 2024). Health data therefore cannot be used for temporal trend analysis.

---

## Statistical Methods

### Descriptive statistics
State rankings and regional comparisons use 2022 as the reference year, as it is the most complete survey wave (2024 figures are provisional).

### Correlation analysis (Q3)
Two correlation approaches are used:

- **Pearson r** — linear correlation between continuous variables; sensitive to outliers
- **Spearman ρ** — rank-based correlation; more robust with the small n = 16 states

Significance threshold: α = 0.05.

### Simple OLS regression (Q3)
`beds_per_1000 ~ income_mean` is fitted via `scipy.stats.linregress`. With n = 16 states this is exploratory only; results should not be over-interpreted.

### East vs West comparison (Q1)
East Malaysia is defined as Sabah, Sarawak, and W.P. Labuan. A two-sample independent t-test compares mean household income between East and West.

### Trend analysis (Q4)
Absolute and percentage changes in `income_mean` and `poverty_absolute` are computed between 2019 and 2024 at state level. National figures are unweighted means across states.

---

## Reference Year Choice

| Analysis | Reference year | Reason |
|---|---|---|
| Cross-sectional ranking (Q1, Q2, Q3) | 2022 | Most complete survey; 2024 is provisional |
| Trend analysis (Q4) | 2019 → 2022 → 2024 | Full time series |
