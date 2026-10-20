from domain.compliance import ComplianceDecision, ComplianceResult

AUDIENCE_RULES = ("audience.status", "audience.email_allowed", "audience.permission_verified")


def check_audience_eligibility(audience: object, traffic_type: str) -> ComplianceResult:
    if getattr(audience, "status", "") != "active":
        return ComplianceResult(ComplianceDecision.BLOCK, ("AUDIENCE_NOT_ACTIVE",), AUDIENCE_RULES)
    if traffic_type == "email" and not getattr(audience, "email_allowed", False):
        return ComplianceResult(
            ComplianceDecision.BLOCK, ("AUDIENCE_EMAIL_NOT_ALLOWED",), AUDIENCE_RULES
        )
    if not getattr(audience, "permission_verified", False):
        return ComplianceResult(ComplianceDecision.BLOCK, ("AUDIENCE_NOT_APPROVED",), AUDIENCE_RULES)
    return ComplianceResult(ComplianceDecision.APPROVE, (), AUDIENCE_RULES)
