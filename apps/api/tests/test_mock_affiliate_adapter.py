import pytest

from integrations.affiliate.mock import MockAffiliateAdapter
from services.offer_ingestion import OfferIngestionService


@pytest.mark.asyncio
async def test_mock_affiliate_adapter_syncs_100_offers():
    adapter = MockAffiliateAdapter()

    offers = await adapter.sync_offers()

    assert len(offers) == 100
    assert all("id" in offer for offer in offers)
    assert any(offer["email_allowed"] is True for offer in offers)
    assert any(offer["email_allowed"] is False for offer in offers)


def test_offer_ingestion_normalizes_offer_payload():
    raw_offer = {
        "id": "offer-1",
        "network_id": "mock",
        "external_offer_id": "ext-1",
        "name": "Healthy Offer",
        "description": "Example offer",
        "advertiser": "Example Brand",
        "category": "finance",
        "geo": "US",
        "payout": 20.0,
        "payout_type": "CPA",
        "epc": 15.5,
        "conversion_rate": 0.04,
        "allowed_traffic_types": ["email", "social"],
        "email_allowed": True,
        "status": "active",
    }

    offer = OfferIngestionService.normalize_offer(raw_offer)

    assert offer.id == "offer-1"
    assert offer.email_allowed is True
    assert offer.allowed_traffic_types == ["email", "social"]
