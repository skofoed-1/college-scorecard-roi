-- QUERY: best_value_per_state
-- Best-value institution (lowest payback_years) in each state, via a window
-- function ranking partitioned by state.
WITH ranked AS (
    SELECT
        state,
        institution,
        payback_years,
        RANK() OVER (PARTITION BY state ORDER BY payback_years ASC) AS state_rank
    FROM institutions
)
SELECT state, institution, ROUND(payback_years, 2) AS payback_years
FROM ranked
WHERE state_rank = 1
ORDER BY payback_years;

-- QUERY: cost_tier_median
-- Median payback years by net-price quartile. Quartiles come from NTILE(4);
-- the median itself is the standard window-function pattern (SQLite has no
-- built-in MEDIAN()): rank each tier's payback_years, then average the
-- middle row for an odd-sized tier or the middle two for an even-sized one.
WITH tiered AS (
    SELECT *, NTILE(4) OVER (ORDER BY net_price) AS cost_tier
    FROM institutions
),
ordered AS (
    SELECT
        cost_tier,
        payback_years,
        ROW_NUMBER() OVER (PARTITION BY cost_tier ORDER BY payback_years) AS rn,
        COUNT(*) OVER (PARTITION BY cost_tier) AS cnt
    FROM tiered
)
SELECT
    cost_tier,
    MAX(cnt) AS institutions,
    ROUND(AVG(payback_years), 2) AS median_payback_years
FROM ordered
WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)
GROUP BY cost_tier
ORDER BY cost_tier;
