from domain.compliance import ComplianceDecision, ComplianceResult

OFFER_RULES = ("offer.status", "offer.email_allowed", "offer.traffic_type", "offer.email_approval")


def check_offer_eligibility(offer: object, traffic_type: str) -> ComplianceResult:
    if getattr(offer, "status", "") != "active":
        return ComplianceResult(ComplianceDecision.BLOCK, ("OFFER_NOT_ACTIVE",), OFFER_RULES)
    if traffic_type == "email" and not getattr(offer, "email_allowed", False):
        return ComplianceResult(ComplianceDecision.BLOCK, ("EMAIL_NOT_ALLOWED",), OFFER_RULES)
    if traffic_type not in getattr(offer, "allowed_traffic_types", []):
        return ComplianceResult(ComplianceDecision.BLOCK, ("TRAFFIC_TYPE_NOT_ALLOWED",), OFFER_RULES)
    if traffic_type == "email" and getattr(offer, "email_approval_required", False):
        return ComplianceResult(ComplianceDecision.REVIEW, ("EMAIL_APPROVAL_REQUIRED",), OFFER_RULES)
    return ComplianceResult(ComplianceDecision.APPROVE, (), OFFER_RULES)
