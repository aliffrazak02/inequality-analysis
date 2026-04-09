-- sqlite_quickstart.sql
-- Copy and run these queries on malaysia_project.db.

-- 1) List all tables in the database
SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;

-- 2) Preview SDI ranking
SELECT state, sdi_score, sdi_rank, double_deprivation
FROM sdi_scores
ORDER BY sdi_rank
LIMIT 16;

-- 3) States with highest poverty in 2024
SELECT state, poverty_absolute
FROM combined_state
WHERE year = 2024
ORDER BY poverty_absolute DESC
LIMIT 10;

-- 4) Health infrastructure ranking by beds per 1000 in 2024
SELECT state, beds_per_1000, facilities_per_100k
FROM health_state
WHERE year = 2024
ORDER BY beds_per_1000 DESC;

-- 5) Join inequality and CPI context in 2024
SELECT
    c.state,
    c.income_median,
    c.poverty_absolute,
    c.gini,
    c.cpi_overall
FROM combined_state c
WHERE c.year = 2024
ORDER BY c.poverty_absolute DESC;
