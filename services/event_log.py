from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from db.models import EventModel


def record_event(
    session: Session,
    event_type: str,
    campaign_id: str,
    *,
    subscriber_id: str | None = None,
    offer_id: str | None = None,
    variant: str | None = None,
    amount: float = 0.0,
    key: str | None = None,
) -> bool:
    """Insert one real event; returns False when `key` was already recorded (idempotent)."""
    stmt = insert(EventModel).values(
        id=uuid.uuid4().hex,
        event_type=event_type,
        campaign_id=campaign_id,
        subscriber_id=subscriber_id,
        offer_id=offer_id,
        variant=variant,
        amount=amount,
        is_simulated=False,
        idempotency_key=key or uuid.uuid4().hex,
        created_at=datetime.now(UTC),
    ).on_conflict_do_nothing(index_elements=["idempotency_key"])
    inserted = session.execute(stmt).rowcount == 1
    session.commit()
    return inserted


def find_event(session: Session, key: str) -> EventModel | None:
    return session.scalar(select(EventModel).where(EventModel.idempotency_key == key))


def sent_key(campaign_id: str, subscriber_id: str) -> str:
    return f"sent:{campaign_id}:{subscriber_id}"
