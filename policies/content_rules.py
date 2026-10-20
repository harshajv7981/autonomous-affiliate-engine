import re

from domain.compliance import ComplianceDecision, ComplianceResult

PROHIBITED_CLAIMS = {
    "guaranteed",
    "guaranteed income",
    "no risk",
    "instant wealth",
    "risk free",
}


def check_content_compliance(subject: str, body: str) -> ComplianceResult:
    # Any dash, slash or underscore counts as a space: "Risk–free" must match "risk free".
    text = re.sub(r"[\W_]+", " ", f"{subject} {body}".lower())
    blocked_terms = sorted(term for term in PROHIBITED_CLAIMS if term in text)
    if blocked_terms:
        reasons = tuple(f"PROHIBITED_CLAIM:{term}" for term in blocked_terms)
        return ComplianceResult(ComplianceDecision.BLOCK, reasons, ("content.prohibited_claims",))
    return ComplianceResult(ComplianceDecision.APPROVE, (), ("content.prohibited_claims",))
