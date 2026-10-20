from app.config import settings
from fastapi import APIRouter

from agents.orchestrator import run_engine

router = APIRouter(prefix="/api/engine", tags=["engine"])


@router.post("/run")
async def run() -> dict:
    """Run the full autonomous loop once on simulated data and return the result."""
    return await run_engine(system_active=settings.system_active)
