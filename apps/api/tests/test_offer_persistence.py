import asyncio

from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import select

from db.models import OfferModel
from services.offer_repository import list_offers
from services.seeding import seed_offers

client = TestClient(app)


def test_offers_persist_and_seeding_is_idempotent(fresh_db):
    first = asyncio.run(seed_offers(fresh_db))
    second = asyncio.run(seed_offers(fresh_db))

    assert first == 100
    assert second == 100  # re-seeding does not duplicate
    rows = list_offers(fresh_db)
    assert all(row.status == "active" for row in rows)


def test_seeding_upserts_on_network_and_external_id(fresh_db):
    # A row with a different primary key but the same (network, external_id)
    # must be updated in place, not duplicated.
    fresh_db.add(OfferModel(
        id="legacy-id", network_id="mock", external_offer_id="ext-1", name="Stale name",
        category="x", geo="US",
    ))
    fresh_db.commit()

    assert asyncio.run(seed_offers(fresh_db)) == 100
    row = fresh_db.scalar(
        select(OfferModel).where(OfferModel.network_id == "mock", OfferModel.external_offer_id == "ext-1")
    )
    assert row.id == "legacy-id"
    assert row.name == "Mock Offer 1"
    assert row.is_simulated is True


def test_offers_api_reads_from_database(_tables, fresh_db):
    asyncio.run(seed_offers(fresh_db))

    response = client.get("/api/offers?limit=5")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 5
    assert all("payout" in offer and "email_allowed" in offer for offer in payload)
    # Ordered by EPC descending (repository contract).
    epcs = [offer["epc"] for offer in payload]
    assert epcs == sorted(epcs, reverse=True)
