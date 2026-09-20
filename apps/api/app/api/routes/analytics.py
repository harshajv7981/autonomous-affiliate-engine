from fastapi import APIRouter

from services.analytics import build_overview

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
def overview() -> dict:
    return build_overview(
        revenue=250.0,
        affiliate_commissions=80.0,
        traffic_cost=30.0,
        email_cost=15.0,
        ai_cost=10.0,
        infrastructure_cost=20.0,
        active_campaigns=4,
        clicks=400,
        conversions=18,
    )
