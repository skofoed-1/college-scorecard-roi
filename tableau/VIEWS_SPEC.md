# Tableau Public workbook spec

Handoff for building a supplementary Tableau Public workbook, linked from the main README as a secondary view. The GitHub Pages site stays the canonical presentation; this isn't a replacement.

Data source: `college_scorecard_tableau_extract.csv` in this folder, one row per institution, 1,515 rows. It's the exact processed table used by the live site, plus a `cost_tier` column already computed with the same quartile boundaries the site's chart uses (`pd.qcut` on `net_price` into 4 bins). Use that column directly rather than re-bucketing in Tableau, so the two presentations don't quietly disagree.

Regenerate the extract any time `data/processed/college_scorecard_roi.csv` changes: `python scripts/build_site_data.py` then re-export `load_roi()`'s output (see how this file was generated in that script).

## Palette

Match the site's colors so the two presentations read as one project:

| Role | Hex |
|---|---|
| Public | `#2a78d6` |
| Private nonprofit | `#eb6834` |
| Cost tier: Low | `#86b6ef` |
| Cost tier: Medium-low | `#5598e7` |
| Cost tier: Medium-high | `#2a78d6` |
| Cost tier: High | `#184f95` |
| In-state (dumbbell) | `#86b6ef` |
| Out-of-state est. (dumbbell) | `#184f95` |

## Views

### 1. Cost vs. earnings

Scatter plot, mirroring the site's main chart.

- X: `net_price`, Y: `median_earnings_10yr`
- Color: `control_label` (Public / Private nonprofit, palette above)
- Tooltip: `institution`, `state`, `payback_years`
- Filter (optional, adds interactivity Tableau does well): a parameter or quick filter on `state` and on `cost_tier`

### 2. Payback years by cost tier

Bar chart.

- X: `cost_tier`, sorted manually Low → Medium-low → Medium-high → High (not alphabetical)
- Y: `MEDIAN(payback_years)` (Tableau supports MEDIAN as a table calc/aggregate directly, unlike the SQLite layer in this repo, which had to hand-roll it)
- Color: `cost_tier`, using the sequential ramp above (darker = higher tier)

### 3. In-state vs. out-of-state (public institutions only)

This is the one view without a direct Tableau-native chart type, so pick whichever you're more comfortable executing:

- **Simpler:** scatter plot, X: `payback_years`, Y: `out_of_state_payback_years_est`, filtered to `control_label = Public`. Add a reference line at Y = X (Analytics pane → reference line → Value: X, or a calculated field `[payback_years]`). Points above the line show the in-state/out-of-state gap directly; the further above the diagonal, the bigger the gap.
- **Closer to the site's dumbbell chart:** a bar-in-bar / Gantt chart with `institution` on rows (filtered to the same top-15-by-gap list as the site, or your own cut), two circle or bar marks for `payback_years` and `out_of_state_payback_years_est`, connected by a Gantt bar. More faithful to the site's chart, more setup.

Either way, the headline stat worth a caption or tooltip: median payback years for public institutions in this table go from 1.10 in-state to 1.96 under the out-of-state estimate, a 78% increase.

## When it's published

Add the link to the main README's intro line, next to the GitHub Pages link, framed as a secondary/alternate view rather than replacing it.
