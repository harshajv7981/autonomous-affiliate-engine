"""Deterministic synthetic audiences and subscribers for $0 simulation.

No real people, no scraped lists: every record is generated from a fixed seed
so runs are reproducible and tests are stable.
"""
from __future__ import annotations

from domain.audiences.audience import Audience
from domain.recipients.recipient import Recipient

AUDIENCE_COUNT = 10
# shortcut: 1,000/audience (not the 1,000-total Phase-3 target) so the expected-value
# funnel yields enough conversions for the optimizer to show real range (SCALE vs
# TEST), matching the 10k-scale example in PROJECT_INSTRUCTIONS section 16.
RECIPIENTS_PER_AUDIENCE = 1000


def build_audiences() -> list[Audience]:
    audiences: list[Audience] = []
    for i in range(1, AUDIENCE_COUNT + 1):
        # Every 4th audience is unverified/not email-permitted so the compliance
        # gate has something to block in the simulation.
        permissioned = i % 4 != 0
        audiences.append(
            Audience(
                id=f"aud-{i}",
                name=f"Segment {i}",
                source_type="owned_newsletter",
                source_provider="internal",
                geo="US" if i % 2 == 0 else "CA",
                category="finance" if i % 2 == 0 else "software",
                estimated_size=RECIPIENTS_PER_AUDIENCE,
                permission_model="single_opt_in",
                permission_verified=permissioned,
                email_allowed=permissioned,
                status="active",
            )
        )
    return audiences


def build_recipients(audiences: list[Audience]) -> list[Recipient]:
    recipients: list[Recipient] = []
    for audience in audiences:
        for j in range(1, RECIPIENTS_PER_AUDIENCE + 1):
            # Deterministic ~5% unsubscribed to exercise suppression.
            unsubscribed = j % 20 == 0
            recipients.append(
                Recipient(
                    id=f"{audience.id}-r{j}",
                    email=f"user{j}@{audience.id}.example.test",
                    audience_id=audience.id,
                    permission_verified=True,
                    unsubscribed=unsubscribed,
                    status="active",
                )
            )
    return recipients
