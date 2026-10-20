"""Idempotent seeding of simulated offers, audiences and subscribers into Postgres.

Re-running is safe: offers/audiences are merged by primary key, and the large
subscriber/consent/suppression sets are inserted only when empty.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from db.models import (
    AudienceModel,
    ConsentRecord,
    OfferModel,
    SubscriberModel,
    SuppressionRecord,
)
from integrations.affiliate.mock import MockAffiliateAdapter
from services.offer_ingestion import OfferIngestionService
from simulator.world import build_audiences, build_recipients


async def seed_offers(session: Session) -> int:
    raw_offers = await MockAffiliateAdapter().sync_offers()
    for raw in raw_offers:
        offer = OfferIngestionService.normalize_offer(raw)
        session.merge(OfferModel(
            id=offer.id,
            network_id=offer.network_id,
            external_offer_id=offer.external_offer_id,
            name=offer.name,
            description=offer.description,
            advertiser=offer.advertiser,
            category=offer.category,
            geo=offer.geo,
            payout=offer.payout,
            payout_type=offer.payout_type,
            epc=offer.epc,
            conversion_rate=offer.conversion_rate,
            allowed_traffic_types=offer.allowed_traffic_types,
            email_allowed=offer.email_allowed,
            email_approval_required=offer.email_approval_required,
            terms_url=offer.terms_url,
            tracking_url_template=offer.tracking_url_template,
            status=offer.status,
        ))
    session.commit()
    return session.scalar(select(func.count()).select_from(OfferModel))


def seed_audiences_and_subscribers(session: Session) -> dict:
    audiences = build_audiences()
    for audience in audiences:
        session.merge(AudienceModel(
            id=audience.id,
            name=audience.name,
            source_type=audience.source_type,
            source_provider=audience.source_provider,
            geo=audience.geo,
            category=audience.category,
            estimated_size=audience.estimated_size,
            permission_model=audience.permission_model,
            permission_verified=audience.permission_verified,
            email_allowed=audience.email_allowed,
            status=audience.status,
        ))
    session.commit()

    already = session.scalar(select(func.count()).select_from(SubscriberModel))
    if not already:
        now = datetime.now(UTC)
        subscribers, consents, suppressions = [], [], []
        for recipient in build_recipients(audiences):
            subscribers.append({
                "id": recipient.id,
                "email": recipient.email,
                "audience_id": recipient.audience_id,
                "permission_verified": recipient.permission_verified,
                "unsubscribed": recipient.unsubscribed,
                "status": recipient.status,
            })
            consents.append({
                "id": uuid.uuid4().hex,
                "subscriber_id": recipient.id,
                "source": "simulator",
                "consent_model": "single_opt_in",
                "consented_at": now,
            })
            if recipient.unsubscribed:
                suppressions.append({
                    "id": uuid.uuid4().hex,
                    "email": recipient.email,
                    "subscriber_id": recipient.id,
                    "reason": "unsubscribed",
                    "created_at": now,
                })
        session.bulk_insert_mappings(SubscriberModel, subscribers)
        session.bulk_insert_mappings(ConsentRecord, consents)
        if suppressions:
            session.bulk_insert_mappings(SuppressionRecord, suppressions)
        session.commit()

    return {
        "audiences": session.scalar(select(func.count()).select_from(AudienceModel)),
        "subscribers": session.scalar(select(func.count()).select_from(SubscriberModel)),
        "consent_records": session.scalar(select(func.count()).select_from(ConsentRecord)),
        "suppression_records": session.scalar(select(func.count()).select_from(SuppressionRecord)),
    }
