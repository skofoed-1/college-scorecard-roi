#!/usr/bin/env python3
"""Builds the cleaned ROI table from the raw College Scorecard institution
CSV. Scope: public and private nonprofit, bachelor's-predominant
institutions (PREDDEG == 3) with non-suppressed cost, earnings, and debt
data: the population where "4-year cost vs. 10-year earnings" is a
coherent, apples-to-apples comparison. Also drops institutions with
undergrad enrollment (UGDS) under 100, since a handful of students can
swing the average sharply at that scale; larger institutions with
extreme-looking payback figures (e.g. Princeton, CUNY schools) are kept
as-is; their low net price is a real effect of aid/subsidized tuition,
not noise.

ROI framing used here: a payback-period estimate (how many years of a
graduate's post-graduation salary it would take to cover the total
4-year cost of attendance) plus a debt-to-earnings ratio as a companion
debt-burden indicator. This is descriptive, not causal: it does not
control for selection effects (who chooses/gets into which school), so
it should be read as "what outcomes are associated with this school,"
not "what this school causes for a given student."
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_CSV = ROOT / "data" / "raw" / "Most-Recent-Cohorts-Institution.csv"
OUT_CSV = ROOT / "data" / "processed" / "college_scorecard_roi.csv"

COLUMNS = [
    "UNITID", "INSTNM", "STABBR", "CONTROL", "PREDDEG",
    "COSTT4_A", "NPT4_PUB", "NPT4_PRIV", "UGDS",
    "C150_4", "MD_EARN_WNE_P10", "GRAD_DEBT_MDN",
]

CONTROL_LABELS = {1: "Public", 2: "Private nonprofit"}

MIN_ENROLLMENT = 100

NUMERIC_COLUMNS = ["COSTT4_A", "NPT4_PUB", "NPT4_PRIV", "UGDS", "C150_4", "MD_EARN_WNE_P10", "GRAD_DEBT_MDN"]


def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RAW_CSV, usecols=COLUMNS, na_values=["NULL", "PrivacySuppressed", "PS"], low_memory=False)
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def build_roi_table(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df["PREDDEG"] == 3]
    df = df[df["CONTROL"].isin(CONTROL_LABELS)]

    df["net_price"] = df["NPT4_PUB"].fillna(df["NPT4_PRIV"])
    df["four_year_cost"] = df["net_price"] * 4

    df = df.dropna(subset=["four_year_cost", "MD_EARN_WNE_P10", "GRAD_DEBT_MDN", "UGDS"])
    df = df[(df["four_year_cost"] > 0) & (df["MD_EARN_WNE_P10"] > 0)]
    df = df[df["UGDS"] >= MIN_ENROLLMENT]

    df["control_label"] = df["CONTROL"].map(CONTROL_LABELS)
    df["payback_years"] = df["four_year_cost"] / df["MD_EARN_WNE_P10"]
    df["debt_to_earnings"] = df["GRAD_DEBT_MDN"] / df["MD_EARN_WNE_P10"]

    result = df[[
        "UNITID", "INSTNM", "STABBR", "control_label",
        "net_price", "COSTT4_A", "four_year_cost", "UGDS", "C150_4",
        "MD_EARN_WNE_P10", "GRAD_DEBT_MDN",
        "payback_years", "debt_to_earnings",
    ]].rename(columns={
        "INSTNM": "institution",
        "STABBR": "state",
        "COSTT4_A": "sticker_cost",
        "UGDS": "enrollment",
        "C150_4": "completion_rate",
        "MD_EARN_WNE_P10": "median_earnings_10yr",
        "GRAD_DEBT_MDN": "median_grad_debt",
    })

    return result.sort_values("payback_years")


def main() -> None:
    df = load_raw()
    roi = build_roi_table(df)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    roi.to_csv(OUT_CSV, index=False)
    print(f"Wrote {len(roi):,} institutions to {OUT_CSV.relative_to(ROOT)}")
    print(roi[["institution", "state", "payback_years", "debt_to_earnings"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
