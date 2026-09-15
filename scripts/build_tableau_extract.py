#!/usr/bin/env python3
"""Builds a Tableau .hyper extract from tableau/college_scorecard_tableau_extract.csv,
so the Tableau Public workbook has a ready-to-use native data source instead of
Tableau re-parsing a raw CSV. Not committed (see tableau/README.md): Hyper files
embed a creation timestamp, so two runs over identical data are never byte-identical.
"""
from pathlib import Path
from tableauhyperapi import (
    HyperProcess, Telemetry, Connection, CreateMode,
    SqlType, TableDefinition, TableName, NOT_NULLABLE, NULLABLE, escape_string_literal,
)

ROOT = Path(__file__).resolve().parent.parent
EXTRACT_CSV = ROOT / "tableau" / "college_scorecard_tableau_extract.csv"
HYPER_PATH = ROOT / "tableau" / "college_scorecard_tableau_extract.hyper"

TABLE_DEF = TableDefinition(
    table_name=TableName("Extract", "institutions"),
    columns=[
        TableDefinition.Column("UNITID", SqlType.big_int(), NOT_NULLABLE),
        TableDefinition.Column("institution", SqlType.text(), NOT_NULLABLE),
        TableDefinition.Column("state", SqlType.text(), NOT_NULLABLE),
        TableDefinition.Column("control_label", SqlType.text(), NOT_NULLABLE),
        TableDefinition.Column("net_price", SqlType.double(), NULLABLE),
        TableDefinition.Column("out_of_state_net_price_est", SqlType.double(), NULLABLE),
        TableDefinition.Column("sticker_cost", SqlType.double(), NULLABLE),
        TableDefinition.Column("four_year_cost", SqlType.double(), NULLABLE),
        TableDefinition.Column("enrollment", SqlType.double(), NULLABLE),
        TableDefinition.Column("completion_rate", SqlType.double(), NULLABLE),
        TableDefinition.Column("median_earnings_10yr", SqlType.double(), NULLABLE),
        TableDefinition.Column("median_grad_debt", SqlType.double(), NULLABLE),
        TableDefinition.Column("payback_years", SqlType.double(), NULLABLE),
        TableDefinition.Column("out_of_state_payback_years_est", SqlType.double(), NULLABLE),
        TableDefinition.Column("debt_to_earnings", SqlType.double(), NULLABLE),
        TableDefinition.Column("cost_tier", SqlType.text(), NULLABLE),
    ],
)


def main() -> None:
    HYPER_PATH.unlink(missing_ok=True)
    with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        with Connection(endpoint=hyper.endpoint, database=HYPER_PATH,
                         create_mode=CreateMode.CREATE_AND_REPLACE) as connection:
            connection.catalog.create_schema("Extract")
            connection.catalog.create_table(TABLE_DEF)
            count = connection.execute_command(
                command=f"COPY {TABLE_DEF.table_name} FROM {escape_string_literal(str(EXTRACT_CSV))} "
                        f"WITH (FORMAT CSV, HEADER)"
            )
    print(f"Wrote {count} rows to {HYPER_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
