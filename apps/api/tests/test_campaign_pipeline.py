from dataclasses import replace

from domain.audiences.audience import Audience
from domain.compliance import ComplianceDecision
from domain.offers.offer import Offer
from policies.campaign_rules import validate_campaign

BASE_OFFER = Offer(
    id="offer-campaign",
    network_id="mock",
    external_offer_id="ext-campaign",
    name="Campaign Offer",
    description="Example campaign offer",
    advertiser="Example advertiser",
    category="finance",
    geo="US",
    payout=25.0,
    payout_type="CPA",
    epc=18.0,
    conversion_rate=0.05,
    allowed_traffic_types=["email"],
    email_allowed=True,
)
BASE_AUDIENCE = Audience(
    id="aud-campaign",
    name="Campaign Audience",
    source_type="email",
    source_provider="mock",
    geo="US",
    category="finance",
    estimated_size=5000,
    permission_model="explicit_opt_in",
    permission_verified=True,
    email_allowed=True,
    status="active",
)


def validate(offer: Offer, audience: Audience):
    return validate_campaign(offer, audience, "Monthly update", "Clear offer details.")


def test_campaign_approved_when_offer_audience_and_content_pass():
    assert validate(BASE_OFFER, BASE_AUDIENCE).decision is ComplianceDecision.APPROVE


def test_campaign_blocked_when_audience_forbids_email():
    result = validate(BASE_OFFER, replace(BASE_AUDIENCE, email_allowed=False))

    assert result.decision is ComplianceDecision.BLOCK
    assert "AUDIENCE_EMAIL_NOT_ALLOWED" in result.reasons


def test_campaign_blocked_when_offer_forbids_email_and_audience_is_paused():
    result = validate(replace(BASE_OFFER, email_allowed=False), replace(BASE_AUDIENCE, status="paused"))

    assert result.decision is ComplianceDecision.BLOCK
    assert {"EMAIL_NOT_ALLOWED", "AUDIENCE_NOT_ACTIVE"} <= set(result.reasons)


def test_campaign_blocked_when_permission_missing():
    result = validate(BASE_OFFER, replace(BASE_AUDIENCE, permission_verified=False))

    assert result.decision is ComplianceDecision.BLOCK
    assert "AUDIENCE_NOT_APPROVED" in result.reasons


def test_campaign_needs_review_when_offer_requires_email_approval():
    result = validate(replace(BASE_OFFER, email_approval_required=True), BASE_AUDIENCE)

    assert result.decision is ComplianceDecision.REVIEW
    assert result.is_sendable is False
