from domain.offers.offer import Offer
from policies.offer_rules import check_offer_eligibility


def test_valid_offer_is_eligible_for_email_traffic():
    offer = Offer(
        id="offer-1",
        network_id="network-1",
        external_offer_id="ext-1",
        name="Test Offer",
        description="Example offer",
        advertiser="Example advertiser",
        category="finance",
        geo="US",
        payout=20.0,
        payout_type="CPA",
        epc=18.0,
        conversion_rate=0.05,
        allowed_traffic_types=["email", "social"],
        email_allowed=True,
    )

    result = check_offer_eligibility(offer, "email", True)

    assert result.allowed is True
    assert result.reason is None


def test_email_forbidden_offer_is_blocked():
    offer = Offer(
        id="offer-2",
        network_id="network-1",
        external_offer_id="ext-2",
        name="Blocked Offer",
        description="Example forbidden offer",
        advertiser="Example advertiser",
        category="finance",
        geo="US",
        payout=15.0,
        payout_type="CPA",
        epc=8.0,
        conversion_rate=0.02,
        allowed_traffic_types=["social"],
        email_allowed=False,
    )

    result = check_offer_eligibility(offer, "email", True)

    assert result.allowed is False
    assert result.reason == "Email traffic is not allowed for this offer"
