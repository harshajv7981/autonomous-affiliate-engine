from domain.compliance import ComplianceDecision, ComplianceResult
from policies.audience_rules import check_audience_eligibility
from policies.content_rules import check_content_compliance
from policies.offer_rules import check_offer_eligibility


def validate_campaign(offer: object, audience: object, subject: str, body: str) -> ComplianceResult:
    results = (
        check_offer_eligibility(offer, "email"),
        check_audience_eligibility(audience, "email"),
        check_content_compliance(subject, body),
    )
    decisions = {result.decision for result in results}
    if ComplianceDecision.BLOCK in decisions:
        decision = ComplianceDecision.BLOCK
    elif ComplianceDecision.REVIEW in decisions:
        decision = ComplianceDecision.REVIEW
    else:
        decision = ComplianceDecision.APPROVE
    return ComplianceResult(
        decision,
        tuple(reason for result in results for reason in result.reasons),
        tuple(rule for result in results for rule in result.evaluated_rules),
    )
