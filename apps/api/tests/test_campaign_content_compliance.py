from agents.campaign_agent.graph import build_campaign
from domain.audiences.audience import Audience
from domain.compliance import ComplianceDecision
from domain.offers.offer import Offer
from policies.campaign_rules import validate_campaign
from policies.content_rules import check_content_compliance


def test_generated_campaign_content_is_validated():
    offer = Offer(
        id="offer-content",
        network_id="mock",
        external_offer_id="ext-content",
        name="Content Offer",
        description="Example content offer",
        advertiser="Example advertiser",
        category="finance",
        geo="US",
        payout=30.0,
        payout_type="CPA",
        epc=20.0,
        conversion_rate=0.06,
        allowed_traffic_types=["email"],
        email_allowed=True,
    )
    audience = Audience(
        id="aud-content",
        name="Content Audience",
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
    campaign = build_campaign(
        offer,
        audience,
        subject_line="A smarter way to manage growth",
        preheader="See what is possible with this offer",
        body="This email contains clear offer information and a defined CTA.",
        cta="Learn more",
    )

    validation = validate_campaign(offer, audience, campaign.subject_line, campaign.body)
    assert campaign.cta == "Learn more"
    assert validation.is_sendable is True


def test_campaign_content_rejected_when_prohibited_claims_present():
    offer = Offer(
        id="offer-bad-content",
        network_id="mock",
        external_offer_id="ext-bad-content",
        name="Bad Content Offer",
        description="Example bad offer",
        advertiser="Example advertiser",
        category="finance",
        geo="US",
        payout=30.0,
        payout_type="CPA",
        epc=20.0,
        conversion_rate=0.06,
        allowed_traffic_types=["email"],
        email_allowed=True,
    )
    audience = Audience(
        id="aud-bad-content",
        name="Bad Content Audience",
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

    subject = "Guaranteed income in 2 days"
    content = "This claim is not allowed and may mislead recipients."
    validation = validate_campaign(offer, audience, subject, content)

    assert validation.decision is ComplianceDecision.BLOCK
    assert "PROHIBITED_CLAIM:guaranteed income" in validation.reasons


def test_prohibited_claims_match_hyphen_and_spacing_variants():
    for claim in ("Risk-free trial", "Risk–free", "Risk—free", "risk_free", "risk/free"):
        assert check_content_compliance(claim, "").is_sendable is False, claim
    assert check_content_compliance("", "Guaranteed\n  income").is_sendable is False
    assert check_content_compliance("A smarter way to grow", "Learn more").is_sendable is True
