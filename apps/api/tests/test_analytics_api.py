import asyncio

from app.main import app
from fastapi.testclient import TestClient

from services.seeding import seed_audiences_and_subscribers, seed_offers

client = TestClient(app)


def _seed(session):
    asyncio.run(seed_offers(session))
    seed_audiences_and_subscribers(session)


def test_analytics_overview_endpoint(fresh_db):
    _seed(fresh_db)  # commits -> visible to the API's own session
    response = client.get("/api/analytics/overview")

    assert response.status_code == 200
    payload = response.json()
    # Numbers are computed from a simulated engine run over the seeded database.
    for key in ("revenue", "net_profit", "roi", "active_campaigns", "clicks", "conversions"):
        assert key in payload
    assert payload["revenue"] > 0
    assert payload["active_campaigns"] > 0


def test_analytics_campaigns_endpoint(fresh_db):
    _seed(fresh_db)
    response = client.get("/api/analytics/campaigns")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["campaigns"]) > 0
    assert all("net_contribution" in row and "action" in row for row in payload["campaigns"])
