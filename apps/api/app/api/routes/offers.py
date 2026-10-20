from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from services.offer_repository import list_offers, serialize_offer

router = APIRouter(prefix="/api/offers", tags=["offers"])


@router.get("")
def list_offers_route(limit: int = 10, db: Session = Depends(get_db)) -> list[dict]:  # noqa: B008  (FastAPI dependency idiom)
    """Serve offers from PostgreSQL (seeded from the mock network)."""
    return [serialize_offer(offer) for offer in list_offers(db, limit=limit)]
