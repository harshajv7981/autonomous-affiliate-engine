from __future__ import annotations

from sqlalchemy import JSON, Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class OfferModel(Base):
    __tablename__ = "offers"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    network_id: Mapped[str] = mapped_column(String, index=True)
    external_offer_id: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String, default="")
    advertiser: Mapped[str] = mapped_column(String, default="")
    category: Mapped[str] = mapped_column(String, index=True)
    geo: Mapped[str] = mapped_column(String, index=True)
    payout: Mapped[float] = mapped_column(Float, default=0.0)
    payout_type: Mapped[str] = mapped_column(String, default="CPA")
    epc: Mapped[float] = mapped_column(Float, default=0.0)
    conversion_rate: Mapped[float] = mapped_column(Float, default=0.0)
    allowed_traffic_types: Mapped[list] = mapped_column(JSON, default=list)
    email_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    email_approval_required: Mapped[bool] = mapped_column(Boolean, default=False)
    terms_url: Mapped[str | None] = mapped_column(String, nullable=True)
    tracking_url_template: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="active", index=True)
