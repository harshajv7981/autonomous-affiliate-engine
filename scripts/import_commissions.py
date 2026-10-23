"""Import a commission report CSV exported from your affiliate network.

    make import-commissions ARGS='--network clickbank --csv ~/Downloads/report.csv'

Re-run with newer reports any time: rows update in place (PENDING -> APPROVED -> PAID).
Override auto-detected columns with --sub-id-column / --amount-column / --id-column /
--status-column if needed.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from db.session import SessionLocal
from services.commission_import import import_commissions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", required=True)
    parser.add_argument("--csv", required=True, type=Path)
    for field in ("id", "sub-id", "amount", "status", "currency"):
        parser.add_argument(f"--{field}-column")
    args = parser.parse_args()

    overrides = {
        key: value for key, value in {
            "external_id": args.id_column, "sub_id": args.sub_id_column, "amount": args.amount_column,
            "status": args.status_column, "currency": args.currency_column,
        }.items() if value
    }
    with args.csv.expanduser().open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    session = SessionLocal()
    try:
        result = import_commissions(session, rows, args.network, overrides)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    finally:
        session.close()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
