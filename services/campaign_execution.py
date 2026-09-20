from __future__ import annotations

from domain.campaigns.campaign import Campaign


def execute_campaign(campaign: Campaign, recipients: list) -> dict:
    eligible = []
    for recipient in recipients:
        if recipient.status == "active" and not recipient.unsubscribed and recipient.permission_verified:
            eligible.append(recipient)
    campaign.state = "SENDING"
    return {"campaign_id": campaign.id, "sent_count": len(eligible), "recipients": [r.email for r in eligible]}


def register_click(campaign_id: str, recipient_id: str) -> dict:
    return {"campaign_id": campaign_id, "recipient_id": recipient_id, "click_id": f"click-{recipient_id}"}


def calculate_revenue(clicks: int, payout_per_conversion: float) -> float:
    return float(clicks * payout_per_conversion)
