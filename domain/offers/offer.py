from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Offer:
    id: str
    network_id: str
    external_offer_id: str
    name: str
    description: str
    advertiser: str
    category: str
    geo: str
    payout: float
    payout_type: str
    epc: float
    conversion_rate: float
    allowed_traffic_types: list[str]
    email_allowed: bool = False
    email_approval_required: bool = False
    terms_url: Optional[str] = None
    tracking_url_template: Optional[str] = None
    status: str = "active"
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    last_synced_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
