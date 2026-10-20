"""Autonomous orchestrator: runs the full affiliate loop end-to-end on the
persisted (seeded) offers, audiences and subscribers by chaining the agents and
deterministic services.

offer -> score -> match audience -> generate creative -> compliance gate ->
send -> simulate funnel -> revenue/cost -> optimizer decision -> aggregate.

Hard rules stay deterministic: the kill switch and the compliance gate can never
be overridden by any agent.
"""
from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from agents.campaign_agent.graph import build_campaign, generate_creative
from agents.offer_agent.graph import score_offer
from agents.optimizer_agent.graph import decide
from db.models import AudienceModel, OfferModel, SubscriberModel
from db.session import SessionLocal
from policies.campaign_rules import validate_campaign
from policies.offer_rules import check_offer_eligibility
from services.analytics import build_overview, calculate_metrics
from services.campaign_execution import execute_campaign
from simulator.events import SimulationRates, simulate_campaign_outcome

# shortcut: flat per-campaign cost model (owned list => $0 traffic); replace with
# measured costs when real infrastructure/API spend exists.
EMAIL_COST_PER_RECIPIENT = 0.0005
AI_COST_PER_CAMPAIGN = 0.02
INFRASTRUCTURE_COST = 1.0  # fixed per run


def _empty_overview() -> dict:
    return build_overview(0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0)


def _load_world(session: Session):
    """ORM rows share the domain dataclasses' attribute names, so the rest of the
    loop (duck-typed) treats them identically."""
    offers = list(session.scalars(select(OfferModel)))
    audiences = list(session.scalars(select(AudienceModel)))
    recipients_by_audience: dict[str, list] = defaultdict(list)
    for subscriber in session.scalars(select(SubscriberModel)):
        recipients_by_audience[subscriber.audience_id].append(subscriber)
    return offers, audiences, recipients_by_audience


async def run_engine(
    system_active: bool = True,
    rates: SimulationRates | None = None,
    session: Session | None = None,
) -> dict:
    # Kill switch (deterministic, never LLM-gated): no load, no send when halted.
    if not system_active:
        return {"status": "halted", "overview": _empty_overview(), "campaigns": [], "blocked": []}

    owns_session = session is None
    session = session or SessionLocal()
    try:
        offers, audiences, recipients_by_audience = _load_world(session)
        return _run(offers, audiences, recipients_by_audience, rates)
    finally:
        if owns_session:
            session.close()


def _run(offers, audiences, recipients_by_audience, rates) -> dict:
    # Offer agent: keep only email-eligible offers, best-scoring first.
    eligible = [
        offer
        for offer in offers
        if offer.email_allowed and check_offer_eligibility(offer, "email").is_sendable
    ]
    eligible.sort(key=lambda o: score_offer(o)["score"], reverse=True)
    offers_by_geo: dict[str, list] = defaultdict(list)
    for offer in eligible:
        offers_by_geo[offer.geo].append(offer)

    campaigns: list[dict] = []
    blocked: list[dict] = []
    totals = {"revenue": 0.0, "email_cost": 0.0, "ai_cost": 0.0, "clicks": 0, "conversions": 0}

    geo_index: dict[str, int] = defaultdict(int)
    for audience in audiences:
        pool = offers_by_geo.get(audience.geo)
        if not pool:
            continue
        # Different offer per audience -> varied economics for the optimizer.
        offer = pool[geo_index[audience.geo] % len(pool)]
        geo_index[audience.geo] += 1

        creative = generate_creative(offer, audience)
        campaign = build_campaign(
            offer, audience, creative["subject"], creative["preheader"],
            creative["body"], creative["cta"],
        )

        # Compliance gate: hard deterministic check before any send.
        decision = validate_campaign(offer, audience, creative["subject"], creative["body"])
        if not decision.is_sendable:
            campaign.state = "BLOCKED"
            blocked.append({
                "campaign_id": campaign.id, "offer_id": offer.id, "audience_id": audience.id,
                "decision": decision.decision.value, "reasons": list(decision.reasons),
            })
            continue

        campaign.approved = True
        sent = execute_campaign(campaign, recipients_by_audience[audience.id], decision)["sent_count"]
        outcome = simulate_campaign_outcome(sent, offer, rates)
        metrics = calculate_metrics(outcome["clicks"], outcome["conversions"], offer.payout)

        revenue = outcome["commission"]
        email_cost = round(sent * EMAIL_COST_PER_RECIPIENT, 4)
        ai_cost = AI_COST_PER_CAMPAIGN
        net = revenue - email_cost - ai_cost
        action = decide(metrics, net)

        totals["revenue"] += revenue
        totals["email_cost"] += email_cost
        totals["ai_cost"] += ai_cost
        totals["clicks"] += outcome["clicks"]
        totals["conversions"] += outcome["conversions"]

        campaigns.append({
            "campaign_id": campaign.id, "name": campaign.name,
            "offer_id": offer.id, "audience_id": audience.id,
            "sent": sent, "clicks": outcome["clicks"], "conversions": outcome["conversions"],
            "cvr": metrics["cvr"], "epc": metrics["epc"],
            "revenue": round(revenue, 2), "cost": round(email_cost + ai_cost, 2),
            "net_contribution": round(net, 2),
            "action": action["action"], "state": "RUNNING",
        })

    overview = build_overview(
        revenue=round(totals["revenue"], 2),
        traffic_cost=0.0,
        email_cost=round(totals["email_cost"], 4),
        ai_cost=round(totals["ai_cost"], 4),
        infrastructure_cost=INFRASTRUCTURE_COST,
        active_campaigns=len(campaigns),
        clicks=totals["clicks"],
        conversions=totals["conversions"],
    )
    return {"status": "active", "overview": overview, "campaigns": campaigns, "blocked": blocked}
