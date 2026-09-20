from agents.offer_agent.graph import score_offer
from domain.offers.offer import Offer


def test_offer_scoring_returns_recommended_action():
    offer = Offer(
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

    result = score_offer(offer)

    assert result["offer_id"] == "offer-3"
    assert result["recommended_action"] in {"TEST", "REVIEW"}
    assert 0.0 <= result["score"] <= 1.0
