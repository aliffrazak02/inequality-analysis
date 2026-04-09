# Data Dictionary

| Source | Datasets | Notes |
|---|---|---|
| [OpenDOSM](https://api.data.gov.my/data-catalogue) | [hh_income_parlimen.csv](../data/raw/hh_income_parlimen.csv), [hh_poverty_parlimen.csv](../data/raw/hh_poverty_parlimen.csv), [hh_income_state.csv](../data/raw/hh_income_state.csv), [hh_poverty_state.csv](../data/raw/hh_poverty_state.csv)<br>[population_state.csv](../data/raw/population_state.csv), [hh_inequality_state.csv](../data/raw/hh_inequality_state.csv), [cpi_state.csv](../data/raw/cpi_state.csv) | CC-BY licence |
| [MoH Malaysia GitHub](https://github.com/MoH-Malaysia/data-resources-public) | [moh_facilities.csv](../data/raw/moh_facilities.csv), [moh_beds.csv](../data/raw/moh_beds.csv) | Malaysian Open Data Licence |
| [World Bank API](https://api.worldbank.org/v2/) | [worldbank_malaysia.csv](../data/raw/worldbank_malaysia.csv) | National-level; CC-BY 4.0 |

## Raw Files (`data/raw/`)

### [hh_income_parlimen.csv](../data/raw/hh_income_parlimen.csv)
**Grain:** parliamentary constituency x survey year

| Column | Type | Description |
|---|---|---|
| `date` | string (YYYY-MM-DD) | Survey reference date; day and month are always 01-01 |
| `state` | string | State name; variant spellings are normalised in ETL |
| `parlimen` | string | Parliamentary constituency name |
| `income_mean` | float | Mean monthly household income (RM) for the constituency |
| `income_median` | float | Median monthly household income (RM) for the constituency |

### [hh_poverty_parlimen.csv](../data/raw/hh_poverty_parlimen.csv)
**Grain:** parliamentary constituency x survey year

| Column | Type | Description |
|---|---|---|
| `date` | string (YYYY-MM-DD) | Survey reference date |
| `state` | string | State name |
| `parlimen` | string | Parliamentary constituency name |
| `poverty_absolute` | float | Absolute poverty incidence (%) - share of households below the national poverty line |

### [hh_income_state.csv](../data/raw/hh_income_state.csv)
**Grain:** state x survey year

Historical official state income series used in [combined_state.csv](../data/clean/combined_state.csv).

| Column | Type | Description |
|---|---|---|
| `date` | string (YYYY-MM-DD) | Survey reference date |
| `state` | string | State name |
| `income_mean` | float | Mean monthly household income (RM) |
| `income_median` | float | Median monthly household income (RM) |

### [hh_poverty_state.csv](../data/raw/hh_poverty_state.csv)
**Grain:** state x survey year

Historical official state poverty series used in [combined_state.csv](../data/clean/combined_state.csv).

| Column | Type | Description |
|---|---|---|
| `date` | string (YYYY-MM-DD) | Survey reference date |
| `state` | string | State name |
| `poverty_absolute` | float | Absolute poverty incidence (%) |
| `poverty_hardcore` | float | Hardcore poverty incidence (%) |
| `poverty_relative` | float | Relative poverty incidence (%) |

### [hh_inequality_state.csv](../data/raw/hh_inequality_state.csv)
**Grain:** state x survey year

Official state-level Gini series used to override the constituency-derived proxy where available.

| Column | Type | Description |
|---|---|---|
| `state` | string | State name |
| `date` | string (YYYY-MM-DD) | Survey reference date |
| `gini` | float | Official household income Gini coefficient |

### [population_state.csv](../data/raw/population_state.csv)
**Grain:** state x age group x sex x ethnicity

| Column | Type | Description |
|---|---|---|
| `date` | string (YYYY-MM-DD) | Census reference date (2020-01-01) |
| `state` | string | State name |
| `age` | string | Age group; the ETL uses the overall total row |
| `sex` | string | Sex category; the ETL uses the overall total row |
| `ethnicity` | string | Ethnic group; the ETL uses the overall total row |
| `population` | float | Population count in thousands (multiply by 1000 for actual count) |

### [cpi_state.csv](../data/raw/cpi_state.csv)
**Grain:** monthly state CPI in wide format

Used by the ETL to build the annual [cpi_state.csv](../data/clean/cpi_state.csv) clean table.

| Column | Type | Description |
|---|---|---|
| `date` | string (YYYY-MM-DD) | Monthly CPI reference date |
| `category` | string | CPI basket category (for example `overall`, `food_beverage`, `transport`) |
| `johor` ... `wp-putrajaya` | float | State-level CPI index columns in wide format (one column per state/federal territory slug) |


### [moh_beds.csv](../data/raw/moh_beds.csv)
**Grain:** individual hospital snapshot (no year column)

| Column | Type | Description |
|---|---|---|
| `hospital` | string | Hospital name |
| `state` | string | State where the hospital is located |
| `beds_nonicu` | float | Number of non-ICU inpatient beds; NaN where not reported |
| `util_nonicu` | float | Non-ICU bed utilisation rate (%) |
| `beds_icu` | float | Number of ICU beds |
| `util_icu` | float | ICU bed utilisation rate (%) |
| `vent` | float | Number of mechanical ventilators |
| `util_vent` | float | Ventilator utilisation rate (%) |

### [moh_facilities.csv](../data/raw/moh_facilities.csv)
**Grain:** individual facility snapshot (no year column)

| Column | Type | Description |
|---|---|---|
| `state` | string | State where the facility is located |
| `district` | string | District within the state |
| `sector` | string | `government` or `private` |
| `type` | string | Facility type, such as `hospital` or `klinik` |
| `name` | string | Facility name |
| `address` | string | Street address |
| `phone` | string | Contact number |
| `lat` | float | Latitude |
| `lon` | float | Longitude |

### [worldbank_malaysia.csv](../data/raw/worldbank_malaysia.csv)
**Grain:** indicator x year (national level)

Supplementary context only; not used in the main analytical tables.

| Column | Type | Description |
|---|---|---|
| `year` | integer | Reference year |
| `life_expectancy` | float | Life expectancy at birth (years) |
| `infant_mortality` | float | Infant mortality rate (per 1000 live births) |
| `health_exp_gdp` | float | Current health expenditure (% of GDP) |
| `hospital_beds` | float | Hospital beds (per 1000 people) |

---

## Clean / Analytical Files (`data/clean/`)

### [combined_state.csv](../data/clean/combined_state.csv)
**Grain:** state x year

This is the main longitudinal socioeconomic table. It combines historical DOSM state series with the recent constituency-derived series and attaches CPI where available.

| Column | Type | Description |
|---|---|---|
| `state_code` | string | ISO-like three-letter state code |
| `state` | string | Canonical state name |
| `year` | integer | Analysis year |
| `territory_type` | string | `state`, `capital`, `admin`, or `island_ft` |
| `income_mean` | float | Mean monthly household income (RM) |
| `income_median` | float | Median monthly household income (RM) |
| `poverty_absolute` | float | Absolute poverty incidence (%) |
| `gini` | float | State Gini series; official DOSM values are used where available |
| `cpi_overall` | float | Annual mean overall CPI; only available for the recent overlap period |

### [health_state.csv](../data/clean/health_state.csv)
**Grain:** state x year

| Column | Type | Description |
|---|---|---|
| `state_code` | string | ISO-like three-letter state code |
| `state` | string | Canonical state name |
| `year` | integer | Analysis year (2019, 2022, 2024) |
| `territory_type` | string | `state`, `capital`, `admin`, or `island_ft` |
| `population` | float | Total state population (actual count) |
| `hospital_count` | integer | Number of facilities classified as `hospital` |
| `facility_count` | integer | Total number of health facilities |
| `beds_nonicu` | float | Total non-ICU inpatient beds |
| `beds_icu` | float | Total ICU beds |
| `beds_total` | float | `beds_nonicu + beds_icu` |
| `beds_per_1000` | float | Hospital beds per 1000 population |
| `facilities_per_100k` | float | Health facilities per 100000 population |

### [sdi_scores.csv](../data/clean/sdi_scores.csv)
**Grain:** state-level 2022 SDI table

| Column | Type | Description |
|---|---|---|
| `state_code` | string | ISO-like three-letter state code |
| `state` | string | Canonical state name |
| `territory_type` | string | State classification used for sensitivity checks |
| `poverty_absolute` | float | Raw poverty input used in SDI |
| `gini` | float | Raw Gini input used in SDI |
| `income_median` | float | Raw income input used in SDI |
| `beds_per_1000` | float | Raw health input used in SDI |
| `facilities_per_100k` | float | Raw health input used in SDI |
| `n_poverty` | float | Min-max normalised poverty component |
| `n_gini` | float | Min-max normalised inequality component |
| `n_income` | float | Inverted and normalised income component |
| `n_beds` | float | Inverted and normalised beds component |
| `n_facilities` | float | Inverted and normalised facilities component |
| `sdi_score` | float | Weighted deprivation score |
| `sdi_rank` | integer | Rank by `sdi_score` |
| `double_deprivation` | boolean | Flag for high socioeconomic and high health deprivation |
| `sdi_rank_no_terr` | integer | Rank after excluding Federal Territories |
| `sdi_score_eq` | float | Equal-weight SDI score |
| `sdi_rank_eq` | integer | Rank by equal-weight SDI score |

### [cpi_national.csv](../data/clean/cpi_national.csv)
**Grain:** year (national level)

Annual national CPI table built from OpenDOSM's national CPI series. Used in `combined_state.csv` to deflate income and as context for the long-run trend analysis.

| Column | Type | Description |
|---|---|---|
| `year` | integer | Annual CPI year |
| `cpi_overall` | float | Annual average overall national CPI |

### [cpi_state.csv](../data/clean/cpi_state.csv)
**Grain:** state x year

| Column | Type | Description |
|---|---|---|
| `state_code` | string | ISO-like three-letter state code |
| `state` | string | Canonical state name |
| `year` | integer | Annual CPI year |
| `cpi_overall` | float | Annual average overall CPI |

---

## State Code Reference

| `state_code` | State | Region |
|---|---|---|
| JHR | Johor | West |
| KDH | Kedah | West |
| KTN | Kelantan | West |
| KUL | W.P. Kuala Lumpur | West |
| LBN | W.P. Labuan | East |
| MLK | Melaka | West |
| NSN | Negeri Sembilan | West |
| PHG | Pahang | West |
| PJY | W.P. Putrajaya | West |
| PLS | Perlis | West |
| PNG | Pulau Pinang | West |
| PRK | Perak | West |
| SBH | Sabah | East |
| SGR | Selangor | West |
| SWK | Sarawak | East |
| TRG | Terengganu | West |
