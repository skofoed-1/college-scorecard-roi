# Tableau Public workbook spec

Handoff for building a supplementary Tableau Public workbook, linked from the main README as a secondary view. The GitHub Pages site stays the canonical presentation; this isn't a replacement.

Data source: `college_scorecard_tableau_extract.csv` in this folder, one row per institution, 1,515 rows. It's the exact processed table used by the live site, plus a `cost_tier` column already computed with the same quartile boundaries the site's chart uses (`pd.qcut` on `net_price` into 4 bins). Use that column directly rather than re-bucketing in Tableau, so the two presentations don't quietly disagree.

A `.hyper` extract of the same data (Tableau's native format, faster to load than a raw CSV import) is available too, built via `python scripts/build_tableau_extract.py`. It's not committed to the repo since Hyper files embed a creation timestamp and are never byte-identical run to run, same reason `sql/college_scorecard_roi.db` isn't committed. Regenerate it locally, or use the CSV directly, whichever's easier from wherever you're running Tableau Desktop.

Regenerate either any time `data/processed/college_scorecard_roi.csv` changes: `python scripts/build_site_data.py` then re-export `load_roi()`'s output for the CSV (see how this file was generated in that script), or `python scripts/build_tableau_extract.py` for the `.hyper` file.

**Building this in the Tableau Public web editor (Tableau Desktop isn't available on Linux):** the web editor's backend session can go stale after sitting idle, which loses the workbook's connection to its data file and, in one case here, lost an entire unsaved workbook. Publish/save early and often rather than working through a long unsaved session. If a data connection breaks, remove it and add a fresh one rather than using "Replace," since Replace tends to reuse the same broken cached metadata.

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

## The "My State" parameter (replaces a separate in-state/out-of-state view)

Rather than a third, standalone chart comparing in-state vs. out-of-state, both views below respond to one parameter, so the whole dashboard becomes personalized to whichever state the viewer picks.

1. **Create parameter `My State`**: String. In the parameter dialog, "Add from Field" → `state`, to pull in all 54 real values automatically. Then manually add one more list entry, `Select your state...`, and set it as the default.
2. **Create two calculated fields:**
   ```
   Net Price (my state)
   IF [state] = [My State] THEN [net_price]
   ELSE [out_of_state_net_price_est]
   END
   ```
   ```
   Payback Years (my state)
   IF [state] = [My State] THEN [payback_years]
   ELSE [out_of_state_payback_years_est]
   END
   ```
   The `Select your state...` placeholder never matches a real state code, so every institution falls through to the out-of-state branch until the viewer actually picks one. No extra "nothing selected" logic needed.
3. Use these calculated fields (not the raw `net_price`/`payback_years` columns) in Views 1 and 2 below.
4. Right-click `My State` in the Data pane → **Show Parameter Control**, and place it once on the dashboard. Because it's a parameter, not a per-sheet filter, one control drives every sheet referencing it.

Worth a caption near the parameter control: private nonprofit institutions won't move no matter what state is picked, since their price doesn't vary by residency, only public institutions' prices change based on whether they're in the selected state. That's correct behavior, not a bug, but it looks odd unexplained.

## Views

### 1. Cost vs. earnings

Scatter plot, mirroring the site's main chart.

- Rows: `AVG(Net Price (my state))`, Columns: `AVG(median_earnings_10yr)` (switch both pills from their default aggregation to Average; at this grain the value is the same either way, but Average reads correctly since these are already institution-level averages, not additive counts)
- Marks card: **Circle**
- `UNITID` → **Detail** (this is what gives one mark per institution instead of one aggregated point across the whole table; use `UNITID` specifically, not `institution`, since it's the guaranteed-unique key)
- Color: `control_label` (Public / Private nonprofit, palette above)
- Tooltip: `institution`, `state`, `payback_years`
- Filter (optional, adds interactivity Tableau does well): a quick filter on `cost_tier`

### 2. Payback years by cost tier

Bar chart.

- X: `cost_tier`, sorted manually Low → Medium-low → Medium-high → High (not alphabetical)
- Y: `MEDIAN(Payback Years (my state))` (Tableau supports MEDIAN as a direct aggregate, unlike the SQLite layer in this repo, which had to hand-roll it via a window-function pattern)
- Color: `cost_tier`, using the sequential ramp above (darker = higher tier)
- Note: `cost_tier` itself stays anchored to the fixed, in-state `net_price` quartiles regardless of the `My State` selection, so the buckets don't shift under you when you change state; only the median payback within each bucket updates.

## When it's published

Add the link to the main README's intro line, next to the GitHub Pages link, framed as a secondary/alternate view rather than replacing it.
