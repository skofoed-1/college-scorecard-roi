# College Scorecard ROI Explorer

**Question:** For a bachelor's degree, how does the total cost of attendance compare to what graduates actually earn afterward, and does that relationship vary a lot by school?

## Method

- **Scope:** public and private nonprofit institutions where a bachelor's degree is the predominant credential (U.S. Dept. of Education's `PREDDEG == 3`), with undergrad enrollment of at least 100 students. For-profit institutions (`CONTROL == 3`) are excluded: their net-price fields (`NPT4_PROG`/`NPT4_OTHER`) don't map onto the public/private-nonprofit cost logic used here, and mixing in a third, differently-measured cost basis would break the apples-to-apples comparison this project is built around.
- **Cost:** average net price (what students actually pay after grants/scholarships, not sticker price) times 4 years. `sticker_cost` (average annual cost of attendance before aid) is included alongside it, so the gap between list price and what students actually pay is visible per institution.
- **Earnings:** median earnings of former students 10 years after enrollment, among those working and not enrolled elsewhere.
- **Metric:** `payback_years` = four-year cost ÷ median 10-year earnings. Roughly, this is how many years of a graduate's post-grad salary it would take to cover the cost of the degree. Lower means the cost recovers faster relative to what graduates go on to earn. A companion `debt_to_earnings` ratio (median graduate debt ÷ median 10-year earnings) captures debt burden specifically, since a school can look fine on payback years while still leaving graduates with a lot of debt relative to income.

## What this is and isn't measuring

This is descriptive, not causal. It doesn't control for who chooses or gets into which school. Students at higher-earning schools may have earned more anywhere, for reasons that have nothing to do with the school itself. Read it as "what outcomes are associated with this school," not "what this school would do for a given student."

A handful of schools show `payback_years` under one year. Checked against enrollment and cohort-size figures, most of these aren't a data error: Princeton and several CUNY schools land here because their net price is genuinely near-zero for most students (large aid budgets, or, for CUNY, low public tuition), combined with strong post-graduation earnings: a real result, not noise. The 100-student enrollment floor above exists only to drop the few institutions small enough that a handful of students can swing the average sharply (e.g. a college with under 100 undergraduates reporting a near-zero net price); it isn't a general claim that low payback years are suspect.

## Data

U.S. Dept. of Education [College Scorecard](https://collegescorecard.ed.gov/data/), institution-level bulk file. Free, no API key, no rate limit.

```
scripts/fetch_data.py       # downloads the current bulk CSV to data/raw/ (not committed, ~96MB)
scripts/build_roi_table.py  # cleans it and computes payback_years / debt_to_earnings
data/processed/college_scorecard_roi.csv   # the resulting table, committed (small)
```

To reproduce: `pip install -r requirements.txt`, then run both scripts in order.

## Status

Data pipeline built, enrollment floor and sticker-cost column added, ROI table generated (1,515 institutions). Analysis/visualization (rankings, distributions, state comparisons) and a published site not yet built.
