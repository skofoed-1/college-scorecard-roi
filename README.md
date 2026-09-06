# College Scorecard ROI Explorer

**[View the live site](https://skofoed-1.github.io/college-scorecard-roi/)**: rankings, charts, and a state-by-state breakdown.

**Question:** For a bachelor's degree, how does the total cost of attendance compare to what graduates actually earn afterward, and does that relationship vary a lot by school?

## Method

- **Scope:** public and private nonprofit institutions where a bachelor's degree is the predominant credential (U.S. Dept. of Education's `PREDDEG == 3`), with undergrad enrollment of at least 100 students. For-profit institutions (`CONTROL == 3`) are excluded: their net-price fields (`NPT4_PROG`/`NPT4_OTHER`) don't map onto the public/private-nonprofit cost logic used here, and mixing in a third, differently-measured cost basis would break the apples-to-apples comparison this project is built around.
- **Cost:** average net price (what students actually pay after grants/scholarships, not sticker price) times 4 years. `sticker_cost` (average annual cost of attendance before aid) is included alongside it, so the gap between list price and what students actually pay is visible per institution. For public institutions, this net price is **in-state only**, per the [College Scorecard glossary](https://collegescorecard.ed.gov/data/glossary/); there's no official out-of-state figure. An `out_of_state_net_price_est` column estimates it as in-state net price plus the sticker-tuition gap between residencies, which assumes grant aid doesn't vary by residency. Treat it as a reasonable approximation, not an official number; private nonprofit tuition doesn't have this problem since it doesn't vary by residency.
- **Earnings:** median earnings of former students 10 years after enrollment, among those working and not enrolled elsewhere.
- **Metric:** `payback_years` = four-year cost ÷ median 10-year earnings. Roughly, this is how many years of a graduate's post-grad salary it would take to cover the cost of the degree. Lower means the cost recovers faster relative to what graduates go on to earn. A companion `debt_to_earnings` ratio (median graduate debt ÷ median 10-year earnings) captures debt burden specifically, since a school can look fine on payback years while still leaving graduates with a lot of debt relative to income.

## What this is and isn't measuring

This is descriptive, not causal. It doesn't control for who chooses or gets into which school. Students at higher-earning schools may have earned more anywhere, for reasons that have nothing to do with the school itself. Read it as "what outcomes are associated with this school," not "what this school would do for a given student."

A handful of schools show `payback_years` under one year. Checked against enrollment and cohort-size figures, most of these aren't a data error: Princeton and several CUNY schools land here because their net price is genuinely near-zero for most students (large aid budgets, or, for CUNY, low public tuition), combined with strong post-graduation earnings: a real result, not noise. The 100-student enrollment floor above exists only to drop the few institutions small enough that a handful of students can swing the average sharply (e.g. a college with under 100 undergraduates reporting a near-zero net price); it isn't a general claim that low payback years are suspect.

## Findings

Splitting institutions into net-price quartiles (low to high cost) shows payback years rising steadily with cost, not staying flat: median payback is 0.93 years in the cheapest quartile, 1.29 in the second, 1.66 in the third, and 2.03 in the priciest. Debt-to-earnings doesn't follow the same clean trend, which is the point of tracking it separately from payback years: a school can recover its cost quickly while still leaving graduates comparatively debt-heavy relative to income.

The worst payback years in the dataset are concentrated in a specific, explainable category: specialized arts and music conservatories (Manhattan School of Music, Berklee College of Music, the New England Conservatory, Ringling College of Art and Design, Juilliard), where net price is high relative to typical post-graduation earnings in those fields. This isn't a data artifact. It's a real, consistent pattern across a whole category of institution.

Because public institutions' net price is in-state only, the payback years shown for them understate the real cost for an out-of-state student. Using the out-of-state estimate instead, median payback years across all 560 public institutions in this table rise from 1.10 to 1.96, a 78% increase. The gap is largest at flagship universities with substantial out-of-state enrollment (Michigan, several UC campuses, Montana, Maine, Oregon), where the in-state number alone would be a misleading stand-in for what most non-resident applicants would actually pay.

Full rankings, the cost-vs-earnings scatter, the in-state/out-of-state comparison, and a per-state breakdown are on [the live site](https://skofoed-1.github.io/college-scorecard-roi/).

## SQL analysis

The same processed table also loads into a SQLite database (`sql/college_scorecard_roi.db`, generated by `scripts/build_sql.py`, not committed since it's a build artifact like `data/raw/`), with the analytical queries in `sql/queries.sql`. This intentionally re-derives two results the pandas pipeline already produces, as a SQL-specific demonstration on the same data rather than a second copy of the real pipeline logic.

Cost-tier medians via `NTILE(4)` for the quartile buckets and a window-function median (SQLite has no built-in `MEDIAN()`):

```sql
WITH tiered AS (
    SELECT *, NTILE(4) OVER (ORDER BY net_price) AS cost_tier
    FROM institutions
),
ordered AS (
    SELECT
        cost_tier, payback_years,
        ROW_NUMBER() OVER (PARTITION BY cost_tier ORDER BY payback_years) AS rn,
        COUNT(*) OVER (PARTITION BY cost_tier) AS cnt
    FROM tiered
)
SELECT cost_tier, MAX(cnt) AS institutions, ROUND(AVG(payback_years), 2) AS median_payback_years
FROM ordered
WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)
GROUP BY cost_tier
ORDER BY cost_tier;
```

```
cost_tier  institutions  median_payback_years
1          379           0.93
2          379           1.29
3          379           1.66
4          378           2.03
```

These medians match the pandas pipeline's cost-tier summary exactly, despite computing the quartiles and the median through entirely different mechanisms: a useful cross-check that both are correct. The second query, a `RANK() OVER (PARTITION BY state ...)` window function finding the best-value institution in each state, is in `sql/queries.sql` alongside this one.

## Data

U.S. Dept. of Education [College Scorecard](https://collegescorecard.ed.gov/data/), institution-level bulk file. Free, no API key, no rate limit.

```
scripts/fetch_data.py       # downloads the current bulk CSV to data/raw/ (not committed, ~96MB)
scripts/build_roi_table.py  # cleans it, applies the enrollment floor, computes payback_years / debt_to_earnings
scripts/build_site_data.py  # computes rankings, state summary, and cost-tier summary
scripts/build_site.py       # generates docs/index.html (the published site)
scripts/build_sql.py        # loads the processed table into sql/college_scorecard_roi.db and runs sql/queries.sql
data/processed/college_scorecard_roi.csv   # the resulting table, committed (small)
```

To reproduce: `pip install -r requirements.txt`, then run the scripts in order. `docs/index.html` rebuilds automatically via GitHub Actions on any push that changes `scripts/**` or `data/processed/**` (the same run also builds `sql/college_scorecard_roi.db`, as a check that the SQL queries still execute, but doesn't commit it).

## Status

Complete: data pipeline, enrollment floor, ROI table (1,515 institutions), analysis, published site, and CI rebuild are all in place.
