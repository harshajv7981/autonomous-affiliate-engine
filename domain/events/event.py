from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class EventType(str, Enum):
    OFFER_SYNCED = "offer.synced"
    CAMPAIGN_APPROVED = "campaign.approved"
    CAMPAIGN_BLOCKED = "campaign.blocked"
    MESSAGE_DELIVERED = "message.delivered"
    CLICK_RECORDED = "click.recorded"
    CONVERSION_RECORDED = "conversion.recorded"
    COMMISSION_RECORDED = "commission.recorded"
    COST_RECORDED = "cost.recorded"


@dataclass(frozen=True)
class DomainEvent:
    event_id: str
    event_type: EventType
    aggregate_id: str
    occurred_at: datetime
    payload: Mapping[str, Any]
    correlation_id: str | None = None
    idempotency_key: str | None = None
