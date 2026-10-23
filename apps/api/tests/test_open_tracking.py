import asyncio

import pytest
from app.config import settings
from app.main import app
from fastapi.testclient import TestClient

from services.real_send import send_test_campaign, subscriber_id_for
from services.seeding import seed_offers

client = TestClient(app)
OWNED = ["me1@example.com", "me2@example.com"]


class FakeMailer:
    def __init__(self):
        self.sent = []

    def send(self, to, subject, text, html, headers):
        self.sent.append({"to": to, "html": html})


@pytest.fixture
def sent(fresh_db, monkeypatch):
    monkeypatch.setattr(settings, "test_recipients", ",".join(OWNED))
    asyncio.run(seed_offers(fresh_db))
    mailer = FakeMailer()
    result = send_test_campaign(fresh_db, mailer, system_active=True, dry_run=False)
    return result, mailer


def test_email_embeds_pixel_and_hidden_preheader(sent):
    result, mailer = sent
    html = mailer.sent[0]["html"]
    assert f"/o/{result['campaign_id']}/" in html and ".gif" in html
    assert 'style="display:none' in html


def test_pixel_records_opens_and_unique_openers(sent):
    result, _ = sent
    url = f"/o/{result['campaign_id']}/{subscriber_id_for(OWNED[0])}.gif"
    for _ in range(3):
        response = client.get(url)
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/gif"
        assert response.content.startswith(b"GIF89a")

    row = next(c for c in client.get("/api/analytics/real").json()["campaigns"]
               if c["campaign_id"] == result["campaign_id"])
    assert (row["opens"], row["unique_openers"]) == (3, 1)


def test_unknown_pixel_returns_image_but_records_nothing(sent):
    assert client.get("/o/nope/nobody.gif").status_code == 200
    assert all(c["opens"] == 0 for c in client.get("/api/analytics/real").json()["campaigns"])


def test_pixel_can_be_disabled(fresh_db, monkeypatch):
    monkeypatch.setattr(settings, "test_recipients", OWNED[0])
    monkeypatch.setattr(settings, "track_opens", False)
    asyncio.run(seed_offers(fresh_db))
    mailer = FakeMailer()
    send_test_campaign(fresh_db, mailer, system_active=True, dry_run=False)
    assert "/o/" not in mailer.sent[0]["html"]
