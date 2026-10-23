"""Send one campaign to your own test inboxes (TEST_RECIPIENTS).

    make send-test        # dry run: shows who would get what, sends nothing
    make send-test-live   # actually sends via SMTP
"""
from __future__ import annotations

import argparse
import json
import sys

from app.config import settings

from db.session import SessionLocal
from services.mailer import SmtpMailer
from services.real_send import send_test_campaign


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--send", action="store_true", help="really send (default is a dry run)")
    args = parser.parse_args()

    mailer = None
    if args.send:
        if not (settings.smtp_username and settings.smtp_password):
            print("SMTP_USERNAME / SMTP_PASSWORD are not set in .env", file=sys.stderr)
            return 1
        mailer = SmtpMailer(
            settings.smtp_host, settings.smtp_port, settings.smtp_username, settings.smtp_password,
            f"{settings.sender_name} <{settings.smtp_username}>",
        )

    session = SessionLocal()
    try:
        result = send_test_campaign(
            session, mailer, system_active=settings.system_active, dry_run=not args.send,
        )
    finally:
        session.close()
    print(json.dumps(result, indent=2))
    return 0 if result["status"] in ("sent", "dry_run") else 1


if __name__ == "__main__":
    sys.exit(main())
