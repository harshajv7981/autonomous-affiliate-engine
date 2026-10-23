from types import SimpleNamespace

from domain.compliance import ComplianceDecision
from policies.send_rules import validate_send


def _offer(**overrides):
    values = {
        "id": "o-1", "status": "active", "email_allowed": True, "allowed_traffic_types": ["email"],
        "email_approval_required": False, "geo": "US",
    }
    return SimpleNamespace(**{**values, **overrides})


def _audience(**overrides):
    values = {"id": "a-1", "status": "active", "email_allowed": True, "permission_verified": True, "geo": "US"}
    return SimpleNamespace(**{**values, **overrides})


def _package(**overrides):
    values = {
        "subject": "Monthly pick", "body": "Clear details.", "subject_variants": ["Monthly pick", "A useful tool"],
        "disclosure": "Affiliate disclosure.", "sender_identity": "Lab <lab@example.test>, 1 Main St",
        "unsubscribe_url": "http://localhost/unsubscribe", "tracking_url": "https://net/track?sub_id=c-1",
    }
    return {**values, **overrides}


def _check(offer=None, audience=None, package=None, already_sent=False, audience_sends=0, cap=1):
    return validate_send(
        offer or _offer(), audience or _audience(), package or _package(),
        already_sent=already_sent, audience_sends=audience_sends, frequency_cap=cap,
    )


def test_complete_package_is_approved():
    result = _check()
    assert result.decision is ComplianceDecision.APPROVE
    assert result.reasons == ()


def test_missing_required_fields_block():
    for field, reason in (
        ("disclosure", "MISSING_DISCLOSURE"),
        ("sender_identity", "MISSING_SENDER_IDENTITY"),
        ("unsubscribe_url", "MISSING_UNSUBSCRIBE"),
        ("tracking_url", "MISSING_TRACKING_URL"),
    ):
        result = _check(package=_package(**{field: None}))
        assert result.decision is ComplianceDecision.BLOCK
        assert reason in result.reasons


def test_geo_mismatch_blocks():
    assert "GEO_MISMATCH" in _check(audience=_audience(geo="CA")).reasons


def test_duplicate_and_frequency_cap_block():
    assert "DUPLICATE_SEND" in _check(already_sent=True).reasons
    assert "FREQUENCY_CAP" in _check(audience_sends=1, cap=1).reasons
    assert _check(audience_sends=1, cap=2).decision is ComplianceDecision.APPROVE


def test_prohibited_claim_in_any_variant_blocks():
    result = _check(package=_package(subject_variants=["Fine subject", "Guaranteed income now"]))
    assert result.decision is ComplianceDecision.BLOCK
    assert any(reason.startswith("PROHIBITED_CLAIM") for reason in result.reasons)


def test_advertiser_approval_required_is_review_not_send():
    result = _check(offer=_offer(email_approval_required=True))
    assert result.decision is ComplianceDecision.REVIEW
    assert result.is_sendable is False


def test_worldwide_offer_matches_any_audience_geo():
    assert _check(offer=_offer(geo="ALL"), audience=_audience(geo="IN")).decision is ComplianceDecision.APPROVE
