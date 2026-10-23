from collections import defaultdict

from app.config import settings
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from agents.orchestrator import run_engine
from db.models import CommissionModel, EventModel
from db.session import get_db
from services.commission_import import CONFIRMED, summarize

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
async def overview() -> dict:
    """Live overview computed from a simulated engine run (no hardcoded numbers)."""
    result = await run_engine(system_active=settings.system_active)
    return result["overview"]


@router.get("/campaigns")
async def campaigns() -> dict:
    result = await run_engine(system_active=settings.system_active)
    return {"campaigns": result["campaigns"], "blocked": result["blocked"]}


@router.get("/real")
def real(db: Session = Depends(get_db)) -> dict:  # noqa: B008
    """Real test sends to owner inboxes. Conversions come from the MOCK network: test only."""
    rows: dict[str, dict] = defaultdict(lambda: {
        "sent": 0, "opens": 0, "unique_openers": set(), "clicks": 0, "unique_clickers": set(), "conversions": 0,
        "test_commission": 0.0, "unsubscribes": 0,
        "variants": defaultdict(lambda: {"sent": 0, "opens": 0, "clicks": 0, "conversions": 0}),
    })
    events = db.scalars(select(EventModel).where(EventModel.is_simulated.is_(False)))
    for event in events:
        row = rows[event.campaign_id]
        variant = row["variants"][event.variant] if event.variant else None
        if event.event_type == "message_sent":
            row["sent"] += 1
            variant["sent"] += 1
        elif event.event_type == "open":
            row["opens"] += 1
            row["unique_openers"].add(event.subscriber_id)
            if variant:
                variant["opens"] += 1
        elif event.event_type == "click":
            row["clicks"] += 1
            row["unique_clickers"].add(event.subscriber_id)
            if variant:
                variant["clicks"] += 1
        elif event.event_type == "conversion":
            row["conversions"] += 1
            row["test_commission"] += event.amount
            if variant:
                variant["conversions"] += 1
        elif event.event_type == "unsubscribe":
            row["unsubscribes"] += 1
    commissions = list(db.scalars(select(CommissionModel).where(CommissionModel.is_simulated.is_(False))))
    confirmed_by_campaign: dict[str, float] = defaultdict(float)
    for commission in commissions:
        if commission.campaign_id and (
            commission.status in CONFIRMED or (commission.status == "REVERSED" and commission.amount < 0)
        ):
            confirmed_by_campaign[commission.campaign_id] += float(commission.amount)
    return {
        "is_simulated": False,
        "conversions_are_test_only": True,
        "opens_are_approximate": True,
        # Real money, from the network's own reports (imported). Only APPROVED/PAID count.
        "earnings": summarize(commissions),
        "campaigns": [
            {
                "campaign_id": campaign_id,
                **{k: v for k, v in row.items() if k not in ("unique_clickers", "unique_openers", "variants")},
                "unique_openers": len(row["unique_openers"]),
                "test_commission": round(row["test_commission"], 2),
                "confirmed_earnings": round(confirmed_by_campaign.get(campaign_id, 0.0), 2),
                "unique_clickers": len(row["unique_clickers"]),
                "variants": {name: dict(counts) for name, counts in row["variants"].items()},
            }
            for campaign_id, row in rows.items()
        ],
    }
