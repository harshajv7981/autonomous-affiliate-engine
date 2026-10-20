from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import OfferModel


def list_offers(session: Session, limit: int | None = None, email_allowed: bool | None = None) -> list[OfferModel]:
    stmt = select(OfferModel).where(OfferModel.status == "active").order_by(OfferModel.epc.desc())
    if email_allowed is not None:
        stmt = stmt.where(OfferModel.email_allowed == email_allowed)
    if limit:
        stmt = stmt.limit(limit)
    return list(session.scalars(stmt))


def serialize_offer(offer: OfferModel) -> dict:
    return {column.name: getattr(offer, column.name) for column in offer.__table__.columns}
