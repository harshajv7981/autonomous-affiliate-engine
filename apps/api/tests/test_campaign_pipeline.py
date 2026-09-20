from domain.offers.offer import Offer
from policies.offer_rules import check_offer_eligibility


class MockAudience:
    def __init__(self, permission_verified: bool = True, email_allowed: bool = True):
        self.permission_verified = permission_verified
        self.email_allowed = email_allowed


def test_campaign_approval_pipeline():
    offer = Offer(
        id="offer-campaign-1",
        network_id="mock",
        external_offer_id="ext-campaign-1",
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
    audience = MockAudience(permission_verified=True, email_allowed=True)

    offer_result = check_offer_eligibility(offer, "email", audience.email_allowed)
    approval = offer_result.allowed and audience.permission_verified

    assert offer_result.allowed is True
    assert approval is True


def test_campaign_blocked_when_permission_missing():
    offer = Offer(
        id="offer-campaign-2",
        network_id="mock",
        external_offer_id="ext-campaign-2",
        name="Campaign Offer 2",
        description="Example blocked campaign offer",
        advertiser="Example advertiser",
        category="finance",
        geo="US",
        payout=20.0,
        payout_type="CPA",
        epc=12.0,
        conversion_rate=0.03,
        allowed_traffic_types=["email"],
        email_allowed=True,
    )
    audience = MockAudience(permission_verified=False, email_allowed=True)

    offer_result = check_offer_eligibility(offer, "email", audience.email_allowed)
    approval = offer_result.allowed and audience.permission_verified

    assert offer_result.allowed is True
    assert approval is False
