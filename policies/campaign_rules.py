from __future__ import annotations

from typing import Optional

from policies.content_rules import check_content_compliance
from policies.offer_rules import check_offer_eligibility


def validate_campaign(offer: object, audience: object, subject: Optional[str] = None, body: Optional[str] = None) -> dict:
    offer_check = check_offer_eligibility(
        offer,
        traffic_type="email",
        email_enabled=getattr(audience, "email_allowed", False),
    )
    audience_permission = getattr(audience, "permission_verified", False)
    content_result = check_content_compliance(subject or "", body or "")
    approved = offer_check.allowed and audience_permission and content_result["approved"]
    return {
        "approved": approved,
        "offer_check": offer_check,
        "audience_permission": audience_permission,
        "content": content_result,
        "decision": "APPROVE" if approved else "REVIEW",
    }
