#!/usr/bin/env python3
"""Loads the processed ROI table into a SQLite database and runs the
analytical queries in sql/queries.sql. This duplicates two aggregates
build_site_data.py already computes in pandas (state rankings, cost-tier
summary) by design: it's a SQL skills demonstration on the same data,
not a second copy of the pipeline's real logic.
"""
import re
import sqlite3
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROI_CSV = ROOT / "data" / "processed" / "college_scorecard_roi.csv"
QUERIES_SQL = ROOT / "sql" / "queries.sql"
DB_PATH = ROOT / "sql" / "college_scorecard_roi.db"


def load_queries() -> dict[str, str]:
    text = QUERIES_SQL.read_text()
    parts = re.split(r"-- QUERY: (\w+)\n", text)[1:]  # drop leading text before first marker
    return {name: sql.strip() for name, sql in zip(parts[0::2], parts[1::2])}


def build_db() -> None:
    df = pd.read_csv(ROI_CSV)
    DB_PATH.unlink(missing_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql("institutions", conn, index=False)


def run_queries() -> dict[str, pd.DataFrame]:
    queries = load_queries()
    with sqlite3.connect(DB_PATH) as conn:
        return {name: pd.read_sql(sql, conn) for name, sql in queries.items()}


def main() -> None:
    build_db()
    results = run_queries()
    for name, result in results.items():
        print(f"\n-- {name} ({len(result)} rows) --")
        print(result.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
