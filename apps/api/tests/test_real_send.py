import asyncio
from urllib.parse import parse_qs, urlparse

import pytest
from app.config import settings
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from agents.orchestrator import run_engine
from db.models import EventModel, SubscriberModel, SuppressionRecord
from services.real_send import TEST_AUDIENCE_ID, send_test_campaign, subscriber_id_for
from services.seeding import seed_audiences_and_subscribers, seed_offers

client = TestClient(app)
OWNED = ["me1@example.com", "me2@example.com"]


class FakeMailer:
    def __init__(self):
        self.sent = []

    def send(self, to, subject, text, html, headers):
        self.sent.append({"to": to, "subject": subject, "text": text, "html": html, "headers": headers})


@pytest.fixture
def world(fresh_db, monkeypatch):
    monkeypatch.setattr(settings, "test_recipients", ", ".join(OWNED))
    asyncio.run(seed_offers(fresh_db))
    seed_audiences_and_subscribers(fresh_db)
    return fresh_db


def _send(db, mailer, system_active=True, dry_run=False):
    return send_test_campaign(db, mailer, system_active=system_active, dry_run=dry_run)


def _count(db, event_type):
    db.expire_all()
    return db.scalar(select(func.count()).select_from(EventModel).where(EventModel.event_type == event_type))


def test_refuses_without_allowlist(world, monkeypatch):
    monkeypatch.setattr(settings, "test_recipients", "")
    mailer = FakeMailer()
    assert _send(world, mailer)["status"] == "refused"
    assert mailer.sent == []


def test_kill_switch_blocks_real_sends(world):
    mailer = FakeMailer()
    assert _send(world, mailer, system_active=False)["status"] == "halted"
    assert mailer.sent == []


def test_dry_run_sends_and_records_nothing(world):
    mailer = FakeMailer()
    result = _send(world, mailer, dry_run=True)
    assert result["status"] == "dry_run"
    assert {r["email"] for r in result["recipients"]} == set(OWNED)
    assert mailer.sent == [] and _count(world, "message_sent") == 0


def test_sends_only_to_allowlisted_owner_inboxes_with_required_parts(world):
    mailer = FakeMailer()
    result = _send(world, mailer)

    assert result["status"] == "sent"
    assert sorted(m["to"] for m in mailer.sent) == sorted(OWNED)  # none of the 10k simulated
    for message in mailer.sent:
        assert "/unsubscribe?subscriber=" in message["text"]
        assert "List-Unsubscribe" in message["headers"]
        assert "Affiliate disclosure" in message["text"]
        assert settings.sender_postal_address in message["text"]
    assert len({m["subject"] for m in mailer.sent}) == 2  # A/B variants
    assert _count(world, "message_sent") == 2


def test_never_resends_a_campaign_and_moves_to_next_offer(world):
    first, second = _send(world, FakeMailer()), _send(world, FakeMailer())
    assert first["campaign_id"] != second["campaign_id"]
    world.expire_all()
    pairs = world.execute(select(EventModel.campaign_id, EventModel.subscriber_id)
                          .where(EventModel.event_type == "message_sent")).all()
    assert len(pairs) == 4 and len(set(pairs)) == 4


def test_click_redirect_and_test_conversion_counted_once(world):
    result = _send(world, FakeMailer())
    campaign_id, subscriber_id = result["campaign_id"], subscriber_id_for(OWNED[0])

    click = client.get(f"/r/{campaign_id}/{subscriber_id}", follow_redirects=False)
    assert click.status_code == 302
    target = urlparse(click.headers["location"])
    assert target.path == "/mock-network/click"
    query = parse_qs(target.query)
    assert len(query["sub_id"][0]) == 16  # short per-click id, echoed back by networks

    page = client.get(f"{target.path}?{target.query}")
    assert page.status_code == 200 and "Complete test purchase" in page.text
    convert = f"/mock-network/convert?offer_id={query['offer_id'][0]}&sub_id={query['sub_id'][0]}"
    assert client.post(convert).status_code == 200
    assert "Already recorded" in client.post(convert).text
    assert _count(world, "click") == 1 and _count(world, "conversion") == 1

    real = client.get("/api/analytics/real").json()
    row = next(c for c in real["campaigns"] if c["campaign_id"] == campaign_id)
    assert (row["sent"], row["clicks"], row["unique_clickers"], row["conversions"]) == (2, 1, 1, 1)
    assert real["conversions_are_test_only"] is True


def test_unsubscribe_needs_confirmation_and_suppresses_future_sends(world):
    result = _send(world, FakeMailer())
    subscriber_id = subscriber_id_for(OWNED[0])
    url = f"/unsubscribe?subscriber={subscriber_id}&campaign={result['campaign_id']}"

    assert client.get(url).status_code == 200  # a link prefetch alone must not unsubscribe
    world.expire_all()
    assert world.get(SubscriberModel, subscriber_id).unsubscribed is False

    assert client.post(url).status_code == 200
    world.expire_all()
    assert world.get(SubscriberModel, subscriber_id).unsubscribed is True
    assert world.scalar(select(func.count()).select_from(SuppressionRecord)
                        .where(SuppressionRecord.subscriber_id == subscriber_id)) == 1

    mailer = FakeMailer()
    _send(world, mailer)
    assert [m["to"] for m in mailer.sent] == [OWNED[1]]


def test_unknown_links_and_unattributed_conversions_are_rejected(world):
    assert client.get("/r/nope/nobody", follow_redirects=False).status_code == 404
    assert client.post("/mock-network/convert?offer_id=mock-offer-1&sub_id=x__y").status_code == 404


def test_simulation_never_includes_owner_inboxes(world):
    _send(world, FakeMailer())
    result = asyncio.run(run_engine(system_active=True, session=world))
    assert TEST_AUDIENCE_ID not in {c["audience_id"] for c in result["campaigns"]}


def test_seeding_still_builds_simulated_world_after_owner_inboxes_exist(fresh_db, monkeypatch):
    monkeypatch.setattr(settings, "test_recipients", OWNED[0])
    asyncio.run(seed_offers(fresh_db))
    _send(fresh_db, FakeMailer(), dry_run=True)  # creates the owner subscriber first

    counts = seed_audiences_and_subscribers(fresh_db)
    assert counts["subscribers"] == 10000 + 1
