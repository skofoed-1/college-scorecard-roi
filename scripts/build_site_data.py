#!/usr/bin/env python3
"""Computes presentation-ready aggregates from the processed ROI table:
overall rankings, a per-state summary, and a summary by net-price cost
tier. build_roi_table.py's job is cleaning/scoping the raw data; this
script's job is preparing what the site (build_site.py) charts. Kept
separate so neither script has to know about the other's concerns.
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROI_CSV = ROOT / "data" / "processed" / "college_scorecard_roi.csv"

COST_TIER_LABELS = ["Low", "Medium-low", "Medium-high", "High"]


def load_roi() -> pd.DataFrame:
    df = pd.read_csv(ROI_CSV)
    df["cost_tier"] = pd.qcut(df["net_price"], q=4, labels=COST_TIER_LABELS)
    return df


def top_bottom_rankings(df: pd.DataFrame, n: int = 25) -> tuple[pd.DataFrame, pd.DataFrame]:
    ranked = df.sort_values("payback_years")
    best = ranked.head(n)
    worst = ranked.tail(n).sort_values("payback_years", ascending=False)
    return best, worst


def state_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("state")
        .agg(
            institutions=("UNITID", "count"),
            median_payback_years=("payback_years", "median"),
            median_earnings_10yr=("median_earnings_10yr", "median"),
            median_net_price=("net_price", "median"),
        )
        .sort_values("median_payback_years")
        .reset_index()
    )


def cost_tier_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("cost_tier", observed=True)
        .agg(
            institutions=("UNITID", "count"),
            median_payback_years=("payback_years", "median"),
            median_debt_to_earnings=("debt_to_earnings", "median"),
            median_net_price=("net_price", "median"),
        )
        .reindex(COST_TIER_LABELS)
        .reset_index()
    )


def main() -> None:
    df = load_roi()
    best, worst = top_bottom_rankings(df)
    print(f"Loaded {len(df):,} institutions.\n")
    print("Best payback_years (top 10 of 25):")
    print(best[["institution", "state", "payback_years"]].head(10).to_string(index=False))
    print("\nWorst payback_years (top 10 of 25):")
    print(worst[["institution", "state", "payback_years"]].head(10).to_string(index=False))
    print("\nState summary (best 10 of full list):")
    print(state_summary(df).head(10).to_string(index=False))
    print("\nCost tier summary:")
    print(cost_tier_summary(df).to_string(index=False))


if __name__ == "__main__":
    main()
