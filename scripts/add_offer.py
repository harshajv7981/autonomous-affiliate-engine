"""Add/update a real affiliate offer.

    make add-offer ARGS='--name "Product X" --network clickbank --payout 35 \
        --url "https://hop.clickbank.net/?affiliate=you&vendor=x&tid={sub_id}" \
        --geo ALL --email-allowed --terms-url https://...'

Only pass --email-allowed after confirming the program permits email promotion.
"""
from __future__ import annotations

import argparse
import sys

from db.session import SessionLocal
from services.real_offers import create_real_offer


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--url", required=True, help="affiliate link with {sub_id} placeholder")
    parser.add_argument("--payout", type=float, required=True, help="commission per sale")
    parser.add_argument("--network", default="manual")
    parser.add_argument("--external-id")
    parser.add_argument("--geo", default="US", help="country code, or ALL for worldwide")
    parser.add_argument("--category", default="general")
    parser.add_argument("--terms-url")
    parser.add_argument("--email-allowed", action="store_true",
                        help="the program's terms explicitly allow email promotion")
    args = parser.parse_args()

    session = SessionLocal()
    try:
        offer = create_real_offer(
            session, name=args.name, url=args.url, payout=args.payout, network=args.network,
            external_id=args.external_id, geo=args.geo, category=args.category,
            email_allowed=args.email_allowed, terms_url=args.terms_url,
        )
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    finally:
        session.close()
    print(f"Saved real offer {offer.id} (email_allowed={offer.email_allowed}, geo={offer.geo})")
    if not offer.email_allowed:
        print("Note: email sends stay BLOCKED until you re-run with --email-allowed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
