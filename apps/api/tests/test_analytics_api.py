from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_analytics_overview_endpoint():
    response = client.get("/api/analytics/overview")

    assert response.status_code == 200
    payload = response.json()
    assert payload["revenue"] == 250.0
    assert payload["net_profit"] == 95.0
    assert payload["active_campaigns"] == 4
