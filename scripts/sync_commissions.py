"""Sync real commissions from a network API (no CSV needed).

    make sync-commissions               # ClickBank, last 30 days
    make sync-commissions ARGS='--days 90'

Safe to run repeatedly (e.g. daily from n8n/cron): rows update in place.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys

from db.session import SessionLocal
from integrations.affiliate.clickbank import ClickBankError
from services.network_sync import sync_clickbank


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    args = parser.parse_args()
    session = SessionLocal()
    try:
        result = asyncio.run(sync_clickbank(session, days=args.days))
    except ClickBankError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    finally:
        session.close()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
