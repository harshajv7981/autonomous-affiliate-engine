"""Idempotent seed entrypoint: `make seed` (requires migrated Postgres)."""
from __future__ import annotations

import asyncio

from db.session import SessionLocal
from services.seeding import seed_audiences_and_subscribers, seed_offers


def main() -> None:
    session = SessionLocal()
    try:
        offer_count = asyncio.run(seed_offers(session))
        counts = seed_audiences_and_subscribers(session)
        print(f"Seeded offers={offer_count}, " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    finally:
        session.close()


if __name__ == "__main__":
    main()
