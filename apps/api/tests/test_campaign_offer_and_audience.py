from domain.audiences.audience import Audience
from domain.offers.offer import Offer
from policies.audience_rules import check_audience_eligibility
from policies.campaign_rules import validate_campaign


def test_campaign_approval_requires_eligible_offer_and_audience():
    offer = Offer(
        id="offer-eligible",
        network_id="mock",
        external_offer_id="ext-eligible",
        name="Eligible Offer",
        description="Valid offer",
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
        id="aud-eligible",
        name="Eligible Audience",
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

    audience_result = check_audience_eligibility(audience, "email")
    campaign_result = validate_campaign(offer, audience)

    assert audience_result["eligible"] is True
    assert campaign_result["approved"] is True
    assert campaign_result["decision"] == "APPROVE"
