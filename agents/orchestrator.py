"""Autonomous orchestrator: runs the full affiliate loop end-to-end on the
persisted (seeded) offers, audiences and subscribers by chaining the agents and
deterministic services.

offer -> score -> match audience -> generate creative + variants + tracking link ->
send compliance gate -> send -> simulate funnel -> revenue/cost -> rates ->
optimizer recommendation -> aggregate.

Hard rules stay deterministic: the kill switch and the compliance gate can never
be overridden by any agent. Every number produced here is SIMULATED.
"""
from __future__ import annotations

from collections import defaultdict

from app.config import settings
from sqlalchemy import select
from sqlalchemy.orm import Session

from agents.campaign_agent.graph import build_campaign, generate_creative, tracking_url
from agents.offer_agent.graph import score_offer
from agents.optimizer_agent.graph import MODE as OPTIMIZER_MODE
from agents.optimizer_agent.graph import decide
from db.models import AudienceModel, OfferModel, SubscriberModel
from db.session import SessionLocal
from policies.offer_rules import check_offer_eligibility
from policies.send_rules import validate_send
from services.analytics import build_overview, calculate_rates
from services.campaign_execution import execute_campaign
from simulator.events import SimulationRates, simulate_campaign_outcome

# shortcut: flat per-campaign cost model (owned list => $0 traffic); replace with
# measured costs when real infrastructure/API spend exists.
EMAIL_COST_PER_RECIPIENT = 0.0005
AI_COST_PER_CAMPAIGN = 0.02
INFRASTRUCTURE_COST = 1.0  # fixed per run

FUNNEL_FIELDS = ("sent", "delivered", "bounces", "opens", "clicks", "conversions", "unsubscribes", "complaints")
LABELS = {"environment": "simulation", "is_simulated": True, "optimizer_mode": OPTIMIZER_MODE}


def _overview(totals: dict, revenue: float, email_cost: float, ai_cost: float,
              infrastructure_cost: float, active_campaigns: int, status: str) -> dict:
    overview = build_overview(
        revenue=round(revenue, 2),
        traffic_cost=0.0,
        email_cost=round(email_cost, 4),
        ai_cost=round(ai_cost, 4),
        infrastructure_cost=infrastructure_cost,
        active_campaigns=active_campaigns,
        clicks=totals.get("clicks", 0),
        conversions=totals.get("conversions", 0),
    )
    return {
        **overview,
        **calculate_rates(totals, overview["revenue"], overview["net_profit"]),
        **{field: totals.get(field, 0) for field in FUNNEL_FIELDS},
        **LABELS,
        "system_status": status,
    }


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
        return {
            "status": "halted",
            "overview": _overview({}, 0.0, 0.0, 0.0, 0.0, 0, "halted"),
            "campaigns": [],
            "blocked": [],
        }

    owns_session = session is None
    session = session or SessionLocal()
    try:
        offers, audiences, recipients_by_audience = _load_world(session)
        return _run(offers, audiences, recipients_by_audience, rates)
    finally:
        if owns_session:
            session.close()


def _run(offers, audiences, recipients_by_audience, rates) -> dict:
    sender_identity = (
        f"{settings.sender_name} <{settings.sender_email}>, {settings.sender_postal_address}"
    )

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
    totals: dict[str, int] = defaultdict(int)
    revenue_total = email_cost_total = ai_cost_total = 0.0
    sent_keys: set[tuple[str, str]] = set()
    audience_sends: dict[str, int] = defaultdict(int)

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
        package = {
            **creative,
            "tracking_url": tracking_url(offer, campaign.id),
            "unsubscribe_url": f"{settings.unsubscribe_base_url}?campaign={campaign.id}",
            "sender_identity": sender_identity,
        }
        campaign.metadata.update(package)

        # Compliance gate: hard deterministic check before any send.
        key = (offer.id, audience.id)
        decision = validate_send(
            offer, audience, package,
            already_sent=key in sent_keys,
            audience_sends=audience_sends[audience.id],
            frequency_cap=settings.frequency_cap_per_run,
        )
        if not decision.is_sendable:
            campaign.state = "BLOCKED"
            blocked.append({
                "campaign_id": campaign.id, "name": campaign.name,
                "offer_id": offer.id, "audience_id": audience.id,
                "decision": decision.decision.value, "reasons": list(decision.reasons),
            })
            continue
        sent_keys.add(key)
        audience_sends[audience.id] += 1

        campaign.approved = True
        sent = execute_campaign(campaign, recipients_by_audience[audience.id], decision)["sent_count"]
        funnel = simulate_campaign_outcome(sent, offer, rates)

        revenue = funnel["commission"]
        email_cost = round(sent * EMAIL_COST_PER_RECIPIENT, 4)
        ai_cost = AI_COST_PER_CAMPAIGN
        net = revenue - email_cost - ai_cost
        campaign_rates = calculate_rates(funnel, revenue, net)
        recommendation = decide({**funnel, **campaign_rates}, net)

        revenue_total += revenue
        email_cost_total += email_cost
        ai_cost_total += ai_cost
        for field in FUNNEL_FIELDS:
            totals[field] += funnel[field]

        campaigns.append({
            "campaign_id": campaign.id, "name": campaign.name,
            "offer_id": offer.id, "audience_id": audience.id,
            **{field: funnel[field] for field in FUNNEL_FIELDS},
            **campaign_rates,
            "revenue": round(revenue, 2), "cost": round(email_cost + ai_cost, 2),
            "net_contribution": round(net, 2),
            "action": recommendation["action"], "action_reason": recommendation["reason"],
            "tracking_url": package["tracking_url"],
            "subject_variants": package["subject_variants"],
            "state": "RUNNING",
            **LABELS,
        })

    overview = _overview(
        totals, revenue_total, email_cost_total, ai_cost_total,
        INFRASTRUCTURE_COST, len(campaigns), "active",
    )
    return {"status": "active", "overview": overview, "campaigns": campaigns, "blocked": blocked}
