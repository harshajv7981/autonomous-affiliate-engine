"""Real sends to owner-controlled test inboxes only.

Guards (all deterministic):
- kill switch must be on;
- recipients must be in the TEST_RECIPIENTS allowlist AND non-simulated;
- the full send compliance gate must APPROVE;
- one message per (campaign, subscriber), ever (idempotency key);
- unsubscribed / suppressed recipients are skipped.
"""
from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime
from html import escape

from app.config import settings
from sqlalchemy import select
from sqlalchemy.orm import Session

from agents.orchestrator import build_send_package, eligible_offers, new_campaign, sender_identity
from db.models import AudienceModel, ConsentRecord, EventModel, OfferModel, SubscriberModel
from policies.send_rules import ANY_GEO, validate_send
from policies.suppression_rules import check_recipient_eligibility
from services.event_log import find_event, record_event, sent_key

TEST_AUDIENCE_ID = "aud-owner-test"
TEST_GEO = "US"


def allowlist() -> list[str]:
    return [email.strip().lower() for email in settings.test_recipients.split(",") if email.strip()]


def subscriber_id_for(email: str) -> str:
    return "owner-" + hashlib.sha256(email.encode()).hexdigest()[:16]


def ensure_test_audience(session: Session, emails: list[str]) -> AudienceModel:
    session.merge(AudienceModel(
        id=TEST_AUDIENCE_ID, name="Owner test inboxes", source_type="owner_test_inbox",
        source_provider="self", geo=TEST_GEO, category="test", estimated_size=len(emails),
        permission_model="owner_controlled", permission_verified=True, email_allowed=True,
        status="active", is_simulated=False,
    ))
    for email in emails:
        sub_id = subscriber_id_for(email)
        if session.get(SubscriberModel, sub_id) is None:  # never resets an unsubscribe
            session.add(SubscriberModel(
                id=sub_id, email=email, audience_id=TEST_AUDIENCE_ID, permission_verified=True,
                unsubscribed=False, status="active", is_simulated=False,
            ))
            session.flush()
            session.add(ConsentRecord(
                id=uuid.uuid4().hex, subscriber_id=sub_id, source="owner_test_inbox",
                consent_model="owner_controlled", consented_at=datetime.now(UTC),
            ))
    session.commit()
    return session.get(AudienceModel, TEST_AUDIENCE_ID)


def render(package: dict, click_url: str, unsubscribe_url: str) -> tuple[str, str]:
    text = (
        f"{package['body']}\n\n{package['cta']}: {click_url}\n\n---\n"
        f"{package['sender_identity']}\nUnsubscribe: {unsubscribe_url}\n"
    )
    body_html = escape(package["body"]).replace("\n", "<br>")
    html = (
        f"<p>{body_html}</p>"
        f'<p><a href="{escape(click_url)}">{escape(package["cta"])}</a></p>'
        f'<hr><p style="font-size:12px;color:#666">{escape(package["sender_identity"])}<br>'
        f'<a href="{escape(unsubscribe_url)}">Unsubscribe</a></p>'
    )
    return text, html


def send_test_campaign(session: Session, mailer, *, system_active: bool, dry_run: bool = True) -> dict:
    if not system_active:
        return {"status": "halted", "reason": "KILL_SWITCH"}
    emails = allowlist()
    if not emails:
        return {"status": "refused", "reason": "TEST_RECIPIENTS is empty"}

    audience = ensure_test_audience(session, emails)
    subscribers = list(session.scalars(
        select(SubscriberModel).where(
            SubscriberModel.audience_id == audience.id, SubscriberModel.is_simulated.is_(False),
        )
    ))

    # Next best offer this audience hasn't received yet -> one new campaign per run.
    already = set(session.scalars(
        select(EventModel.campaign_id).where(
            EventModel.event_type == "message_sent",
            EventModel.subscriber_id.in_([s.id for s in subscribers]),
        )
    ))
    # Real offers (your own affiliate links) take priority; mock offers are only a
    # fallback for testing the pipeline before you have one.
    offers = list(session.scalars(select(OfferModel)))
    real = [offer for offer in offers if not offer.is_simulated]
    pool = eligible_offers(real) if real else eligible_offers(offers)
    if real and not pool:
        return {"status": "blocked", "reason": "real offers exist but none allow email "
                "(re-add with --email-allowed once the program terms permit it)"}
    candidates = [
        offer for offer in pool
        if offer.geo in (ANY_GEO, audience.geo) and new_campaign(offer, audience).id not in already
    ]
    if not candidates:
        return {"status": "exhausted", "reason": "every eligible offer was already sent"}
    offer = candidates[0]
    campaign = new_campaign(offer, audience)
    from_email = settings.smtp_username or settings.sender_email
    package = build_send_package(offer, audience, campaign, sender_identity(from_email))

    decision = validate_send(
        offer, audience, package,
        already_sent=False, audience_sends=0, frequency_cap=settings.frequency_cap_per_run,
    )
    if not decision.is_sendable:
        return {"status": "blocked", "campaign_id": campaign.id, "reasons": list(decision.reasons)}

    base = settings.public_base_url
    results = []
    for index, subscriber in enumerate(subscribers):
        # Hard guards, independent of anything above.
        if subscriber.is_simulated or subscriber.email.lower() not in emails:
            continue
        if not check_recipient_eligibility(subscriber).is_sendable:
            results.append({"email": subscriber.email, "status": "skipped_suppressed"})
            continue
        key = sent_key(campaign.id, subscriber.id)
        if find_event(session, key):
            continue
        variant = "AB"[index % 2]
        subject = package["subject_variants"][index % 2]
        click_url = f"{base}/r/{campaign.id}/{subscriber.id}"
        unsubscribe_url = f"{base}/unsubscribe?subscriber={subscriber.id}&campaign={campaign.id}"
        text, html = render(package, click_url, unsubscribe_url)
        if not dry_run:
            mailer.send(
                subscriber.email, subject, text, html,
                {"List-Unsubscribe": f"<{unsubscribe_url}>"},
            )
            record_event(
                session, "message_sent", campaign.id, subscriber_id=subscriber.id,
                offer_id=offer.id, variant=variant, key=key,
            )
        results.append({"email": subscriber.email, "variant": variant, "subject": subject,
                        "status": "sent" if not dry_run else "would_send"})

    return {
        "status": "dry_run" if dry_run else "sent",
        "campaign_id": campaign.id,
        "offer": offer.name,
        "offer_is_real": not offer.is_simulated,
        "recipients": results,
    }
