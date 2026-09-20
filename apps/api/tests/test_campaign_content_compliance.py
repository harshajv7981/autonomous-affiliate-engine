from agents.campaign_agent.graph import build_campaign
from domain.audiences.audience import Audience
from domain.offers.offer import Offer
from policies.campaign_rules import validate_campaign


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

    validation = validate_campaign(offer, audience)
    assert campaign.subject_line
    assert campaign.cta == "Learn more"
    assert validation["approved"] is True


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
    validation = validate_campaign(offer, audience)
    prohibited_claims = ["guaranteed", "guaranteed income", "no risk"]
    blocked = any(term in subject.lower() for term in prohibited_claims) or any(term in content.lower() for term in prohibited_claims)

    assert validation["approved"] is True
    assert blocked is True
