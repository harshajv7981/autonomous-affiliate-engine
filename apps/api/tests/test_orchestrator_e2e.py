import asyncio

from agents.orchestrator import run_engine
from services.seeding import seed_audiences_and_subscribers, seed_offers


def _seed(session):
    asyncio.run(seed_offers(session))
    seed_audiences_and_subscribers(session)


def test_full_loop_produces_revenue_and_decisions(fresh_db):
    _seed(fresh_db)
    result = asyncio.run(run_engine(system_active=True, session=fresh_db))

    assert result["status"] == "active"
    assert len(result["campaigns"]) > 0
    assert result["overview"]["revenue"] > 0
    assert all(c["action"] for c in result["campaigns"])
    assert result["overview"]["conversions"] == sum(c["conversions"] for c in result["campaigns"])


def test_every_output_is_labelled_simulated_with_tracking(fresh_db):
    _seed(fresh_db)
    result = asyncio.run(run_engine(system_active=True, session=fresh_db))

    overview = result["overview"]
    assert overview["is_simulated"] is True and overview["environment"] == "simulation"
    assert overview["optimizer_mode"] == "recommendation"
    assert "net_contribution_per_1000" in overview
    for campaign in result["campaigns"]:
        assert campaign["is_simulated"] is True
        # sub_id ties network conversions back to this campaign.
        assert f"sub_id={campaign['campaign_id']}" in campaign["tracking_url"]
        assert len(campaign["subject_variants"]) >= 2


def test_compliance_gate_blocks_unpermissioned_audiences(fresh_db):
    _seed(fresh_db)
    result = asyncio.run(run_engine(system_active=True, session=fresh_db))

    # Unverified/non-email audiences (every 4th) must be blocked, never sent.
    assert len(result["blocked"]) > 0
    sent_audiences = {c["audience_id"] for c in result["campaigns"]}
    blocked_audiences = {b["audience_id"] for b in result["blocked"]}
    assert sent_audiences.isdisjoint(blocked_audiences)


def test_kill_switch_halts_everything():
    # No DB touched when halted.
    result = asyncio.run(run_engine(system_active=False))

    assert result["status"] == "halted"
    assert result["campaigns"] == []
    assert result["overview"]["revenue"] == 0.0
    assert result["overview"]["system_status"] == "halted"
