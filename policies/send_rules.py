"""Final deterministic gate before any send. AI output can never override a BLOCK."""
from domain.compliance import ComplianceDecision, ComplianceResult
from policies.campaign_rules import validate_campaign
from policies.content_rules import check_content_compliance

ANY_GEO = "ALL"  # worldwide offers (common for digital products) match every audience

SEND_RULES = (
    "send.geo_match",
    "send.disclosure",
    "send.sender_identity",
    "send.unsubscribe",
    "send.tracking_url",
    "send.duplicate",
    "send.frequency_cap",
    "send.subject_variants",
)

REQUIRED_FIELDS = (
    ("disclosure", "MISSING_DISCLOSURE"),
    ("sender_identity", "MISSING_SENDER_IDENTITY"),
    ("unsubscribe_url", "MISSING_UNSUBSCRIBE"),
    ("tracking_url", "MISSING_TRACKING_URL"),
)


def validate_send(
    offer: object,
    audience: object,
    package: dict,
    *,
    already_sent: bool,
    audience_sends: int,
    frequency_cap: int,
) -> ComplianceResult:
    base = validate_campaign(offer, audience, package.get("subject", ""), package.get("body", ""))
    blocking: list[str] = []

    if getattr(offer, "geo", None) not in (ANY_GEO, getattr(audience, "geo", None)):
        blocking.append("GEO_MISMATCH")
    blocking += [reason for field, reason in REQUIRED_FIELDS if not package.get(field)]
    if already_sent:
        blocking.append("DUPLICATE_SEND")
    if audience_sends >= frequency_cap:
        blocking.append("FREQUENCY_CAP")
    for variant in package.get("subject_variants", []):
        blocking += check_content_compliance(variant, "").reasons

    if blocking or base.decision is ComplianceDecision.BLOCK:
        decision = ComplianceDecision.BLOCK
    else:
        decision = base.decision  # APPROVE or REVIEW (REVIEW never sends)
    return ComplianceResult(
        decision,
        tuple(dict.fromkeys(base.reasons + tuple(blocking))),
        base.evaluated_rules + SEND_RULES,
    )
