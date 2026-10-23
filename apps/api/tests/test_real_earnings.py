import asyncio
from decimal import Decimal
from urllib.parse import parse_qs, urlparse

import pytest
from app.config import settings
from app.main import app
from fastapi.testclient import TestClient

from services.commission_import import import_commissions, normalize_status, parse_amount
from services.real_offers import create_real_offer
from services.real_send import send_test_campaign, subscriber_id_for
from services.seeding import seed_audiences_and_subscribers, seed_offers

client = TestClient(app)
OWNED = ["me1@example.com", "me2@example.com"]
REAL_URL = "https://network.example/hop?aff=me&tid={sub_id}"


class FakeMailer:
    def __init__(self):
        self.sent = []

    def send(self, to, subject, text, html, headers):
        self.sent.append(to)


@pytest.fixture
def world(fresh_db, monkeypatch):
    monkeypatch.setattr(settings, "test_recipients", ",".join(OWNED))
    asyncio.run(seed_offers(fresh_db))
    seed_audiences_and_subscribers(fresh_db)
    return fresh_db


def _real_offer(db, **overrides):
    values = {"name": "Real Product", "url": REAL_URL, "payout": 35.0, "network": "testnet",
              "geo": "ALL", "email_allowed": True}
    return create_real_offer(db, **{**values, **overrides})


def _send(db):
    return send_test_campaign(db, FakeMailer(), system_active=True, dry_run=False)


def _click(campaign_id, email):
    response = client.get(f"/r/{campaign_id}/{subscriber_id_for(email)}", follow_redirects=False)
    assert response.status_code == 302
    return response.headers["location"]


@pytest.mark.parametrize("url", [
    "http://network.example/?tid={sub_id}",     # not https
    "https://network.example/?tid=fixed",       # no placeholder
    "https://network.example/?tid={sub_id}&x={other}",
])
def test_rejects_bad_affiliate_urls(world, url):
    with pytest.raises(ValueError):
        _real_offer(world, url=url)


def test_real_offer_without_email_permission_is_never_sent(world):
    _real_offer(world, email_allowed=False)
    result = _send(world)
    assert result["status"] == "blocked"


def test_real_offer_takes_priority_and_click_goes_to_network_with_click_id(world):
    _real_offer(world)
    result = _send(world)
    assert result["status"] == "sent" and result["offer_is_real"] is True

    location = _click(result["campaign_id"], OWNED[0])
    target = urlparse(location)
    assert location.startswith("https://network.example/hop")
    assert len(parse_qs(target.query)["tid"][0]) == 16


def test_import_attributes_updates_and_nets_refunds(world):
    _real_offer(world)
    result = _send(world)
    click_id = parse_qs(urlparse(_click(result["campaign_id"], OWNED[0])).query)["tid"][0]

    report = [
        {"Transaction ID": "T1", "TID": click_id, "Commission": "$35.00", "Status": "pending"},
        {"Transaction ID": "T2", "TID": "not-ours", "Commission": "10.00", "Status": "approved"},
        {"Transaction ID": "", "TID": click_id, "Commission": "5", "Status": "approved"},  # invalid
    ]
    counts = import_commissions(world, report, "testnet")
    assert counts == {"rows": 3, "attributed": 1, "unattributed": 1, "invalid": 1}

    earnings = client.get("/api/analytics/real").json()["earnings"][0]
    assert (earnings["confirmed"], earnings["pending"]) == (10.0, 35.0)

    # Newer report: T1 approved (updates in place, no duplicate) ...
    import_commissions(world, [{"Transaction ID": "T1", "TID": click_id, "Commission": "35.00",
                                "Status": "approved"}], "testnet")
    real = client.get("/api/analytics/real").json()
    assert real["earnings"][0]["confirmed"] == 45.0
    row = next(c for c in real["campaigns"] if c["campaign_id"] == result["campaign_id"])
    assert row["confirmed_earnings"] == 35.0

    # ... then refunded as a separate negative row: nets back out.
    import_commissions(world, [{"Transaction ID": "T1", "TID": click_id, "Commission": "-35.00",
                                "Status": "RFND"}], "testnet")
    earnings = client.get("/api/analytics/real").json()["earnings"][0]
    assert earnings["confirmed"] == 10.0 and earnings["reversed"] == 35.0


def test_status_and_amount_parsing():
    assert normalize_status("Approved") == "APPROVED"
    assert normalize_status("RFND") == "REVERSED"
    assert normalize_status("something new") == "PENDING"  # never assumed confirmed
    assert parse_amount("$1,234.50") == Decimal("1234.50")


def test_missing_columns_are_reported(world):
    with pytest.raises(ValueError, match="Could not find columns"):
        import_commissions(world, [{"foo": "1"}], "testnet")
