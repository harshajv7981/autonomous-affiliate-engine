import asyncio

from app.main import app
from fastapi.testclient import TestClient

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
