#!/usr/bin/env python3
"""Builds docs/index.html: a static, self-contained page presenting the
ROI findings (cost-vs-earnings scatter, payback-by-cost-tier bar chart,
rankings tables, state summary) via Plotly-generated HTML. No JS is
hand-written; Plotly's built-in hover tooltips and legend-click toggling
are the interaction layer, per the plan's decision to avoid a separate
frontend stack.
"""
import plotly.graph_objects as go
from pathlib import Path

from build_site_data import load_roi, top_bottom_rankings, state_summary, cost_tier_summary, COST_TIER_LABELS

ROOT = Path(__file__).resolve().parent.parent
OUT_HTML = ROOT / "docs" / "index.html"

# Categorical slots 1 (blue) and 2 (orange) from the portfolio's validated
# palette, assigned in fixed order (Public first, Private nonprofit second).
CONTROL_COLORS = {"Public": "#2a78d6", "Private nonprofit": "#eb6834"}

# Sequential blue ramp, ordinal steps (darker = higher tier), one per cost tier.
TIER_COLORS = {"Low": "#86b6ef", "Medium-low": "#5598e7", "Medium-high": "#2a78d6", "High": "#184f95"}

INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"

LAYOUT_DEFAULTS = dict(
    paper_bgcolor=SURFACE,
    plot_bgcolor=SURFACE,
    font=dict(family="system-ui, -apple-system, 'Segoe UI', sans-serif", color=INK, size=13),
    margin=dict(l=60, r=30, t=50, b=50),
)


def build_scatter(df) -> go.Figure:
    fig = go.Figure()
    for label in ["Public", "Private nonprofit"]:
        sub = df[df["control_label"] == label]
        fig.add_trace(go.Scatter(
            x=sub["net_price"],
            y=sub["median_earnings_10yr"],
            mode="markers",
            name=label,
            marker=dict(size=6, color=CONTROL_COLORS[label], opacity=0.65),
            customdata=sub[["institution", "state"]],
            hovertemplate="<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
                          "Net price: $%{x:,.0f}<br>Median earnings (10yr): $%{y:,.0f}<extra></extra>",
        ))
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title="Net price vs. median earnings, 10 years after entry",
        xaxis=dict(title="Average annual net price ($)", gridcolor=GRID, tickprefix="$"),
        yaxis=dict(title="Median earnings, 10yr ($)", gridcolor=GRID, tickprefix="$"),
        legend=dict(title="Institution type"),
        height=520,
    )
    return fig


def build_tier_bar(tiers) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=tiers["cost_tier"],
        y=tiers["median_payback_years"],
        marker_color=[TIER_COLORS[t] for t in tiers["cost_tier"]],
        hovertemplate="%{x} cost tier<br>Median payback: %{y:.2f} years<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title="Median payback years by net-price cost tier",
        xaxis=dict(title="Net-price cost tier (quartiles, low to high)", categoryorder="array",
                   categoryarray=COST_TIER_LABELS, gridcolor=GRID),
        yaxis=dict(title="Median payback years", gridcolor=GRID),
        height=420,
        showlegend=False,
    )
    return fig


def table_html(df, columns, headers, formatters) -> str:
    rows = []
    for _, row in df.iterrows():
        cells = "".join(f"<td>{formatters[c](row[c])}</td>" for c in columns)
        rows.append(f"<tr>{cells}</tr>")
    head = "".join(f"<th>{h}</th>" for h in headers)
    return f'<table class="data-table"><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def money(v) -> str:
    return f"${v:,.0f}"


def years(v) -> str:
    return f"{v:.2f}"


def build_page(scatter_html, tier_html, best_table, worst_table, state_table) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>College Scorecard ROI Explorer</title>
<style>
  body {{ margin: 0; padding: 0 1.5rem 3rem; background: {SURFACE}; color: {INK};
         font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }}
  .wrap {{ max-width: 960px; margin: 0 auto; }}
  h1 {{ font-size: 1.6rem; margin-top: 2rem; }}
  h2 {{ font-size: 1.15rem; margin-top: 2.5rem; color: {INK}; }}
  p.lede {{ color: {MUTED}; max-width: 70ch; }}
  .table-scroll {{ max-height: 420px; overflow-y: auto; border: 1px solid {GRID}; border-radius: 6px; }}
  table.data-table {{ border-collapse: collapse; width: 100%; font-size: 0.9rem; }}
  table.data-table th, table.data-table td {{ padding: 6px 10px; text-align: right; border-bottom: 1px solid {GRID}; }}
  table.data-table th:first-child, table.data-table td:first-child {{ text-align: left; }}
  table.data-table thead th {{ position: sticky; top: 0; background: {SURFACE}; color: {MUTED};
                                font-weight: 600; font-size: 0.8rem; text-transform: uppercase; }}
  .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
  @media (max-width: 800px) {{ .two-col {{ grid-template-columns: 1fr; }} }}
  footer {{ color: {MUTED}; font-size: 0.85rem; margin-top: 3rem; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>College Scorecard ROI Explorer</h1>
  <p class="lede">For a bachelor's degree, how does the cost of attendance compare to what graduates
     actually earn afterward? Public and private-nonprofit institutions, U.S. Dept. of Education
     College Scorecard data. Methodology and scope: see the
     <a href="https://github.com/skofoed-1/college-scorecard-roi">repo README</a>.</p>

  <h2>Cost vs. earnings</h2>
  {scatter_html}

  <h2>Payback years by cost tier</h2>
  {tier_html}

  <h2>Best and worst payback years</h2>
  <div class="two-col">
    <div>
      <p class="lede">Best (top 25)</p>
      <div class="table-scroll">{best_table}</div>
    </div>
    <div>
      <p class="lede">Worst (top 25)</p>
      <div class="table-scroll">{worst_table}</div>
    </div>
  </div>

  <h2>By state</h2>
  <p class="lede">Sorted by median payback years. States with only a handful of qualifying institutions
     (see the "Institutions" column) are volatile rankings driven by one or two schools, not a real
     state-level effect. Read those rows with that in mind.</p>
  <div class="table-scroll">{state_table}</div>

  <footer>Generated from College Scorecard bulk data. See the repo for methodology, scope decisions, and the underlying pipeline.</footer>
</div>
</body>
</html>"""


def main() -> None:
    df = load_roi()
    best, worst = top_bottom_rankings(df)
    tiers = cost_tier_summary(df)
    states = state_summary(df)

    scatter_html = build_scatter(df).to_html(full_html=False, include_plotlyjs="cdn",
                                              config={"displaylogo": False}, div_id="scatter-chart")
    tier_html = build_tier_bar(tiers).to_html(full_html=False, include_plotlyjs=False,
                                               config={"displaylogo": False}, div_id="tier-chart")

    rank_formatters = {"institution": str, "state": str, "payback_years": years}
    best_table = table_html(best, ["institution", "state", "payback_years"],
                             ["Institution", "State", "Payback years"], rank_formatters)
    worst_table = table_html(worst, ["institution", "state", "payback_years"],
                              ["Institution", "State", "Payback years"], rank_formatters)

    state_formatters = {
        "state": str, "institutions": str,
        "median_payback_years": years, "median_earnings_10yr": money, "median_net_price": money,
    }
    state_table = table_html(states, list(state_formatters.keys()),
                              ["State", "Institutions", "Median payback years", "Median earnings (10yr)", "Median net price"],
                              state_formatters)

    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(build_page(scatter_html, tier_html, best_table, worst_table, state_table))
    print(f"Wrote {OUT_HTML.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
