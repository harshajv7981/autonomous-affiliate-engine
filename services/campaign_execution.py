from __future__ import annotations

import uuid

from domain.campaigns.campaign import Campaign
from domain.compliance import ComplianceResult
from policies.suppression_rules import check_recipient_eligibility


def execute_campaign(campaign: Campaign, recipients: list, compliance: ComplianceResult) -> dict:
    if not compliance.is_sendable:
        raise ValueError(f"Campaign {campaign.id} is not approved: {compliance.reasons}")
    eligible = [
        recipient
        for recipient in recipients
        if recipient.audience_id == campaign.audience_id
        and check_recipient_eligibility(recipient).is_sendable
    ]
    campaign.state = "SENDING"
    return {"campaign_id": campaign.id, "sent_count": len(eligible), "recipients": [r.email for r in eligible]}


def register_click(campaign_id: str, recipient_id: str) -> dict:
    return {"campaign_id": campaign_id, "recipient_id": recipient_id, "click_id": f"click-{uuid.uuid4().hex}"}


def calculate_revenue(conversions: int, payout_per_conversion: float) -> float:
    return float(conversions * payout_per_conversion)
