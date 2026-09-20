from fastapi import APIRouter

from integrations.affiliate.mock import MockAffiliateAdapter
from services.offer_ingestion import OfferIngestionService

router = APIRouter(prefix="/api/offers", tags=["offers"])


@router.get("")
async def list_offers() -> list[dict]:
    adapter = MockAffiliateAdapter()
    raw_offers = await adapter.sync_offers()
    return [OfferIngestionService.normalize_offer(item).__dict__ for item in raw_offers[:10]]


@router.post("/sync")
async def sync_offers() -> dict[str, str]:
    adapter = MockAffiliateAdapter()
    await adapter.sync_offers()
    return {"status": "synced"}
