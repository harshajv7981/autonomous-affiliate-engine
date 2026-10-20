from dataclasses import replace

from agents.offer_agent.graph import score_offer
from domain.offers.offer import Offer

STRONG_OFFER = Offer(
    id="offer-3",
    network_id="network-1",
    external_offer_id="ext-3",
    name="High Value Offer",
    description="Strong offer",
    advertiser="Example advertiser",
    category="finance",
    geo="US",
    payout=50.0,
    payout_type="CPA",
    epc=35.0,
    conversion_rate=0.09,
    allowed_traffic_types=["email"],
    email_allowed=True,
)


def test_strong_offer_is_recommended_for_test():
    result = score_offer(STRONG_OFFER)

    assert result["offer_id"] == "offer-3"
    assert result["recommended_action"] == "TEST"
    assert 0.0 <= result["score"] <= 1.0


def test_weak_offer_is_sent_to_review():
    offer = replace(STRONG_OFFER, id="offer-weak", epc=2.0, conversion_rate=0.01)

    result = score_offer(offer)

    assert result["recommended_action"] == "REVIEW"
