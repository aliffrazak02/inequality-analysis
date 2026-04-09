# Methodology

## Research Questions

1. **Income and poverty landscape** - Which states are richest and most deprived?
2. **Health infrastructure** - Which states are best and worst served per capita?
3. **Inequality versus health** - Does income inequality predict poorer health infrastructure?
4. **Trends over time** - How did income and poverty change between 2019 and 2024?

The notebooks also include a supplementary SDI analysis that combines socioeconomic and health deprivation into a single state-level index.

---

## Unit Of Analysis

The primary unit of analysis is the Malaysian state. The clean tables retain all 16 state-level units used in the project, with Federal Territories tagged separately through `territory_type`.

Raw data at finer grains - parliamentary constituency, facility, hospital, or monthly CPI series - is aggregated to state level before analysis.

---

## Data Pipeline

The production workflow is driven by `scripts/run_pipeline.py`, while the notebooks mirror the same steps for exploration and reporting.

```
data/raw/  ->  notebook/01_acquire_data.ipynb  ->  notebook/02_etl.ipynb  ->  data/clean/
```

| Notebook or script | Purpose |
|---|---|
| `scripts/run_pipeline.py` | End-to-end acquire, transform, and export pipeline |
| `notebook/01_acquire_data.ipynb` | Downloads and caches raw files; records acquisition metadata |
| `notebook/02_etl.ipynb` | Validates raw inputs, builds clean tables, and exports CSV / Excel / SQLite outputs |
| `notebook/03_eda.ipynb` | Runs descriptive analysis, rankings, correlations, and trend plots |
| `notebook/04_sdi_analysis.ipynb` | Builds and interprets the Socioeconomic Deprivation Index |

The ETL exports four clean CSV files, one Excel workbook, and one SQLite database.

---

## Socioeconomic Table Construction

Two DOSM source layers are used:

| Source file | Role |
|---|---|
| `hh_income_parlimen.csv` | Recent constituency-level income data |
| `hh_poverty_parlimen.csv` | Recent constituency-level poverty data |
| `hh_income_state.csv` | Historical official state income series |
| `hh_poverty_state.csv` | Historical official state poverty series |
| `hh_inequality_state.csv` | Official state Gini series, used where available |

The recent constituency series is aggregated to state-year level in `combined_state.csv` using simple means across parliamentary constituencies.

| Output column | Rule |
|---|---|
| `income_mean` | Mean of constituency income means within the state |
| `income_median` | Mean of constituency income medians within the state |
| `poverty_absolute` | Mean of constituency poverty rates within the state |
| `gini` | Gini coefficient over constituency income means, measuring inter-constituency dispersion |
| `territory_type` | State classification used for Federal Territory sensitivity checks |
| `cpi_overall` | Annual mean of state CPI where the monthly CPI series overlaps |

Historical DOSM values are merged into the same `combined_state.csv` panel for the long-run series, and official DOSM Gini values replace the proxy where the state-level series is available.

Gini formula used for the constituency-derived proxy:

$$G = \frac{2 \sum_{i=1}^{n} i \cdot x_i}{n \sum_{i=1}^{n} x_i} - \frac{n+1}{n}$$

where $x_i$ are the sorted constituency income means.

---

## Health Infrastructure Table Construction

| Source file | Role |
|---|---|
| `moh_facilities.csv` | Point-in-time facility snapshot |
| `moh_beds.csv` | Point-in-time hospital bed snapshot |
| `population_state.csv` | 2020 census denominator for per-capita measures |

The health clean table is built as a state-year panel in `health_state.csv`.

| Output column | Derivation |
|---|---|
| `hospital_count` | Count of facilities where `type == "hospital"` |
| `facility_count` | Count of all facility records |
| `beds_nonicu` | Sum of non-ICU beds across all hospitals in the state |
| `beds_icu` | Sum of ICU beds across all hospitals in the state |
| `beds_total` | `beds_nonicu + beds_icu` |
| `beds_per_1000` | `beds_total / (population / 1000)` |
| `facilities_per_100k` | `facility_count / (population / 100000)` |
| `territory_type` | State classification used for sensitivity checks |

Because the MOH source files have no year dimension, the same infrastructure counts are replicated across 2019, 2022, and 2024. Only the population denominator varies by analysis year.

---

## CPI Table Construction

The state CPI series is built from `cpi_state.csv`.

| Source pattern | Transformation |
|---|---|
| Monthly CPI by state and category | Filter to the `overall` category |
| Wide state columns | Melt to long format |
| Monthly observations | Average to annual `cpi_overall` values |

The resulting `cpi_state.csv` is a short recent series and is used mainly as context for the combined economic panel.

---

## Statistical Methods

### Descriptive statistics
State rankings and regional comparisons use 2022 as the reference year because it is the most complete survey wave. The 2024 socioeconomic wave is still provisional.

### Correlation analysis
Two correlation approaches are used for the inequality versus health question:

- Pearson r - linear correlation between continuous variables; sensitive to outliers
- Spearman rho - rank-based correlation; more robust with the small state sample

Significance threshold: alpha = 0.05.

### Simple OLS regression
`beds_per_1000 ~ income_mean` is fitted via `scipy.stats.linregress`. With only 16 states this is exploratory and should not be over-interpreted.

### East versus West comparison
East Malaysia is defined as Sabah, Sarawak, and W.P. Labuan. A two-sample independent t-test compares mean household income between East and West.

### Trend analysis
Recent trend analysis uses the 2019, 2022, and 2024 socioeconomic waves in `combined_state.csv`. Long-run trend work uses the historical DOSM state panel embedded in the same file.

### SDI analysis
The Socioeconomic Deprivation Index is computed for 2022 only, using the weights defined in `scripts/config.py`:

- `n_poverty`
- `n_gini`
- `n_income`
- `n_beds`
- `n_facilities`

Each component is min-max normalised to [0, 1] before being combined into a weighted score. The notebook also reports two sensitivity checks: a no-federal-territories ranking and an equal-weight variant.

---

## Reference Year Choice

| Analysis | Reference year | Reason |
|---|---|---|
| Cross-sectional ranking (Q1, Q2, Q3) | 2022 | Most complete survey wave |
| Trend analysis (Q4) | 2019 -> 2022 -> 2024 | Recent time series |
| SDI analysis | 2022 | Same reference year used in the ETL and SDI notebook |
