# Data Dictionary

**COSC 301 Project — Malaysia State-Level Socioeconomic & Health Outcomes**

---

## Raw Files (`data/raw/`)

### `hh_income_parlimen.csv`
Source: Department of Statistics Malaysia (DOSM)
Grain: parliamentary constituency × survey year

| Column | Type | Description |
|---|---|---|
| `date` | string (YYYY-MM-DD) | Survey reference date; day and month are always 01-01 |
| `state` | string | State name (may contain variant spellings — normalised in ETL) |
| `parlimen` | string | Parliamentary constituency name |
| `income_mean` | float | Mean monthly household income (RM) for the constituency |
| `income_median` | float | Median monthly household income (RM) for the constituency |

**Rows:** 666 | **Years covered:** 2019, 2022, 2024 | **States:** 16

---

### `hh_poverty_parlimen.csv`
Source: Department of Statistics Malaysia (DOSM)
Grain: parliamentary constituency × survey year

| Column | Type | Description |
|---|---|---|
| `date` | string (YYYY-MM-DD) | Survey reference date |
| `state` | string | State name |
| `parlimen` | string | Parliamentary constituency name |
| `poverty_absolute` | float | Absolute poverty incidence (%) — share of households below the national poverty line |

**Rows:** 666 | **Years covered:** 2019, 2022, 2024 | **States:** 16

---

### `population_state.csv`
Source: Department of Statistics Malaysia (DOSM), 2020 Population Census
Grain: state × age group × sex × ethnicity

| Column | Type | Description |
|---|---|---|
| `date` | string (YYYY-MM-DD) | Census reference date (2020-01-01) |
| `state` | string | State name |
| `age` | string | Age group; use `"overall_age"` for total |
| `sex` | string | `"overall_sex"`, `"male"`, or `"female"` |
| `ethnicity` | string | Ethnic group; use `"overall_ethnicity"` for total |
| `population` | float | Population count in **thousands** (multiply by 1 000 for actual count) |

**Rows:** 1 000 | **Year covered:** 2020 only

---

### `moh_beds.csv`
Source: Ministry of Health Malaysia (MOH)
Grain: individual hospital (point-in-time snapshot, no year column)

| Column | Type | Description |
|---|---|---|
| `hospital` | string | Hospital name |
| `state` | string | State where the hospital is located |
| `beds_nonicu` | float | Number of non-ICU inpatient beds; NaN where not reported |
| `util_nonicu` | float | Non-ICU bed utilisation rate (%); NaN where not reported |
| `beds_icu` | float | Number of ICU beds |
| `util_icu` | float | ICU bed utilisation rate (%) |
| `vent` | float | Number of mechanical ventilators |
| `util_vent` | float | Ventilator utilisation rate (%) |

**Note:** This is a snapshot dataset. Last updated ~2024 per source commit history. No historical series is available.

---

### `moh_facilities.csv`
Source: Ministry of Health Malaysia (MOH)
Grain: individual facility (point-in-time snapshot, no year column)

| Column | Type | Description |
|---|---|---|
| `state` | string | State where the facility is located |
| `district` | string | District within the state |
| `sector` | string | `"government"` or `"private"` |
| `type` | string | Facility type (e.g., `"hospital"`, `"klinik"`) |
| `name` | string | Facility name |
| `address` | string | Street address |
| `phone` | string | Contact number |
| `lat` | float | Latitude |
| `lon` | float | Longitude |

**Note:** Snapshot dataset, last updated ~2024. No year column.

---

### `worldbank_malaysia.csv`
Source: World Bank Open Data
Grain: indicator × year (national level)

Acquired for supplementary context; not used in the primary analysis tables.

---

## Clean / Analytical Files (`data/clean/`)

### `socioeconomic_state.csv`
Grain: state × year (2019, 2022, 2024) | **16 states × 3 years = 48 rows**

| Column | Type | Description |
|---|---|---|
| `state_code` | string | ISO 3166-2:MY three-letter state code (primary key component) |
| `state` | string | Canonical state name |
| `year` | integer | Survey year (2019, 2022, 2024) |
| `income_mean` | float | Mean monthly household income (RM) — unweighted mean across constituencies |
| `income_median` | float | Median monthly household income (RM) — unweighted mean across constituencies |
| `poverty_absolute` | float | Absolute poverty incidence (%) — unweighted mean across constituencies |
| `gini` | float | Inter-constituency Gini coefficient (0 = perfect equality, 1 = maximum inequality) |
| `parlimen_count` | integer | Number of parliamentary constituencies in the state |

**Primary key:** (`state_code`, `year`)

---

### `health_state.csv`
Grain: state × year (2019, 2022, 2024) | **16 states × 3 years = 48 rows**

| Column | Type | Description |
|---|---|---|
| `state_code` | string | ISO 3166-2:MY three-letter state code |
| `state` | string | Canonical state name |
| `year` | integer | Analysis year (2019, 2022, 2024) — **health values are identical across years** (see Caveats) |
| `population` | float | Total state population (actual count) — from 2020 Census, used as proxy for all years |
| `hospital_count` | integer | Number of facilities classified as `type == "hospital"` |
| `facility_count` | integer | Total number of all health facilities |
| `beds_nonicu` | float | Total non-ICU inpatient beds |
| `beds_icu` | float | Total ICU beds |
| `beds_total` | float | `beds_nonicu + beds_icu` |
| `beds_per_1000` | float | Hospital beds per 1 000 population |
| `facilities_per_100k` | float | Health facilities per 100 000 population |

**Primary key:** (`state_code`, `year`)

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
| PKN | Perlis | West |
| PNG | Pulau Pinang | West |
| PRK | Perak | West |
| SBH | Sabah | East |
| SGR | Selangor | West |
| SWK | Sarawak | East |
| TRG | Terengganu | West |
