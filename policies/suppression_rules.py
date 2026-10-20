from domain.compliance import ComplianceDecision, ComplianceResult

RECIPIENT_RULES = ("recipient.status", "recipient.unsubscribed", "recipient.permission_verified")


def check_recipient_eligibility(recipient: object) -> ComplianceResult:
    if getattr(recipient, "status", "") != "active":
        return ComplianceResult(ComplianceDecision.BLOCK, ("RECIPIENT_NOT_ACTIVE",), RECIPIENT_RULES)
    if getattr(recipient, "unsubscribed", False):
        return ComplianceResult(ComplianceDecision.BLOCK, ("SUPPRESSED",), RECIPIENT_RULES)
    if not getattr(recipient, "permission_verified", False):
        return ComplianceResult(
            ComplianceDecision.BLOCK, ("RECIPIENT_PERMISSION_NOT_VERIFIED",), RECIPIENT_RULES
        )
    return ComplianceResult(ComplianceDecision.APPROVE, (), RECIPIENT_RULES)
