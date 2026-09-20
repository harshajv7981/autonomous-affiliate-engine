from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class OfferRuleResult:
    allowed: bool
    reason: Optional[str] = None


def check_offer_eligibility(offer: object, traffic_type: str, email_enabled: bool) -> OfferRuleResult:
    if getattr(offer, "status", "") != "active":
        return OfferRuleResult(False, "Offer is not active")
    if email_enabled and not getattr(offer, "email_allowed", False):
        return OfferRuleResult(False, "Email traffic is not allowed for this offer")
    if traffic_type not in getattr(offer, "allowed_traffic_types", []):
        return OfferRuleResult(False, "Traffic type is not permitted")
    if getattr(offer, "email_approval_required", False) and email_enabled:
        return OfferRuleResult(False, "Email approval is required")
    return OfferRuleResult(True)
