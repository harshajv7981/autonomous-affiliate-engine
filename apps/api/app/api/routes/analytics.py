from app.config import settings
from fastapi import APIRouter

from agents.orchestrator import run_engine

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
