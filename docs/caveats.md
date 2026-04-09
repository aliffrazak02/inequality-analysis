# Caveats and Limitations

## 1. MOH Health Data Is a Point-in-Time Snapshot

`moh_facilities.csv` and `moh_beds.csv` do not contain a year or date column. The source repository history suggests they reflect health infrastructure as of roughly late 2023 to 2024.

The ETL notebook and pipeline treat these files as a static snapshot and replicate the same infrastructure counts across all analysis years in `health_state.csv`.

**Impact**:

| Question | **Impact** |
|---|---|
| Q1 - Income and poverty | None - uses socioeconomic data only |
| Q2 - Health infrastructure | Low - the ranking is still valid, but it reflects a single snapshot |
| Q3 - Inequality versus health | Moderate - 2022 income is compared with a near-2024 infrastructure snapshot |
| Q4 - Short-term trends | None - health is not used for time-series trend analysis |
| Q5 - Long-run trends | None - handled separately in the historical state series |

**Mitigation**: health infrastructure is treated as a cross-sectional baseline, not a time series.


## 2. Population Denominators Come From the 2020 Census

- `population_state.csv` is a single 2020 census snapshot. There is no 2019 or 2024 population series in the project.

- Per-capita health metrics therefore use the 2020 population as a proxy for all analysis years. This slightly understates 2019 rates and slightly overstates 2024 rates, but the effect is small relative to the state-to-state differences being compared.

- **Mitigation**: the 2020 population is treated as an acceptable approximation for the 2022 reference year used in cross-sectional health analysis.


## 3. CPI Is Supplementary and Short-Ranged

- `cpi_state.csv` is an annualised summary of monthly state CPI data. The ETL filters the `overall` category and averages the monthly values to produce `cpi_overall`.

- This series is only available for a short recent window, so it is used as context in `combined_state.csv` and the EDA notebook rather than as a full inflation-adjustment framework for the whole project.

- **Mitigation**: the project does not rely on CPI to deflate the entire historical income series.


## 4. Gini Measures Inter-Constituency Dispersion

- The `gini` column in the recent constituency-derived data measures dispersion of constituency mean incomes within each state. It is not a household-level Gini coefficient.

- This is an ecological inequality measure. It is useful for describing geographic dispersion, but it should not be compared directly with published DOSM household-level Gini figures.

- **Mitigation**: the variable is kept as `gini` for consistency, but it is interpreted in the docs and analysis as inter-constituency inequality.


## 5. Constituency Aggregation Uses Unweighted Means

- State-level `income_mean`, `income_median`, and `poverty_absolute` are computed as simple means across parliamentary constituencies.

- That means a small rural constituency receives the same weight as a large urban one. This can slightly bias the state aggregates when population is unevenly distributed across constituencies.

- **Mitigation**: constituency-level population weights are not available in the source data, so population-weighted aggregation is not feasible here.


## 6. 2024 Socioeconomic Data Is Provisional

- DOSM labels the 2024 Household Income Survey data as provisional. Values may be revised in later releases.

- **Impact**: the 2019 to 2024 trend analysis uses a provisional endpoint, so the 2024 change estimates should be read as indicative rather than final.

- **Mitigation**: cross-sectional rankings use 2022 as the reference year.


## 7. Small Sample Size For Correlation Analysis

- With only 16 states, the correlation and regression work has low statistical power. A Pearson or Spearman correlation with n = 16 needs a fairly large effect size to be significant at the 0.05 level.

- Implication: a non-significant result does not mean there is no relationship, and a significant result can still be sensitive to a single influential state such as W.P. Kuala Lumpur.

- **Mitigation**: both Pearson and Spearman correlations are reported, and the OLS model is treated as exploratory.


## 8. 2020 and 2021 Are Missing From the Socioeconomic Survey Series

- There is no DOSM Household Income and Expenditure Survey wave for 2020 or 2021 because fieldwork was interrupted during the pandemic.

- **Impact**: the recent socioeconomic series jumps from 2019 to 2022 and then to 2024, so the pandemic shock and recovery path cannot be observed continuously at state level.

- **Mitigation**: the long-run DOSM state series confirms the same gap, and the trend charts annotate it explicitly.


## 9. Historical State Data and Constituency-Derived Data Are Different Series

The project now uses two different state-level economic series:

| Series | Source | Method |
|---|---|---|
| `combined_state` historical years | Official DOSM state tables | Population-weighted DOSM methodology |
| `combined_state` recent years | Constituency-level HIES | Unweighted mean of constituency measures |

The values for overlapping years can differ because the aggregation logic is not the same. The historical DOSM figures are the authoritative series for long-run comparison.

- **Mitigation**: the long-run trend work uses the historical DOSM series, while the recent cross-sectional work uses the constituency-derived series.


## 10. Federal Territories Need Separate Interpretation

W.P. Kuala Lumpur, W.P. Putrajaya, and W.P. Labuan are Federal Territories, not ordinary states. Their demographic and administrative profiles make direct comparison with states imperfect.

The project handles them through the `territory_type` field in the clean tables:

| Territory | Classification | Treatment |
|---|---|---|
| W.P. Kuala Lumpur | `capital` | Retained, because it is an economically important urban outlier |
| W.P. Putrajaya | `admin` | Excluded from the main analysis set because it is a purpose-built administrative enclave |
| W.P. Labuan | `island_ft` | Retained and grouped with East Malaysia |

The `territory_type` column is included in the clean tables so these cases can be filtered or reweighted in sensitivity checks.
