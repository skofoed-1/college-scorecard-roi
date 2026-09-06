# College Scorecard ROI Explorer

**Question:** For a bachelor's degree, how does the total cost of attendance compare to what graduates actually earn afterward, and does that relationship vary a lot by school?

## Method

- **Scope:** public and private nonprofit institutions where a bachelor's degree is the predominant credential (U.S. Dept. of Education's `PREDDEG == 3`). This keeps the comparison apples-to-apples: a 4-year cost estimate next to a "10 years after entry" earnings figure only makes sense for schools where a 4-year degree is the typical outcome.
- **Cost:** average net price (what students actually pay after grants/scholarships, not sticker price) times 4 years.
- **Earnings:** median earnings of former students 10 years after enrollment, among those working and not enrolled elsewhere.
- **Metric:** `payback_years` = four-year cost ÷ median 10-year earnings. Roughly, this is how many years of a graduate's post-grad salary it would take to cover the cost of the degree. Lower means the cost recovers faster relative to what graduates go on to earn. A companion `debt_to_earnings` ratio (median graduate debt ÷ median 10-year earnings) captures debt burden specifically, since a school can look fine on payback years while still leaving graduates with a lot of debt relative to income.

## What this is and isn't measuring

This is descriptive, not causal. It doesn't control for who chooses or gets into which school. Students at higher-earning schools may have earned more anywhere, for reasons that have nothing to do with the school itself. Read it as "what outcomes are associated with this school," not "what this school would do for a given student."

## Data

U.S. Dept. of Education [College Scorecard](https://collegescorecard.ed.gov/data/), institution-level bulk file. Free, no API key, no rate limit.

```
scripts/fetch_data.py       # downloads the current bulk CSV to data/raw/ (not committed, ~96MB)
scripts/build_roi_table.py  # cleans it and computes payback_years / debt_to_earnings
data/processed/college_scorecard_roi.csv   # the resulting table, committed (small)
```

To reproduce: `pip install -r requirements.txt`, then run both scripts in order.

## Status

Data pipeline built and the ROI table generated. Analysis/visualization (rankings, distributions, state comparisons) not yet built.
