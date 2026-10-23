from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String, false
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class EventModel(Base):
    """Real (non-simulated) tracking events: message_sent, click, conversion, unsubscribe."""

    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    event_type: Mapped[str] = mapped_column(String, index=True)
    campaign_id: Mapped[str] = mapped_column(String, index=True)
    subscriber_id: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    offer_id: Mapped[str | None] = mapped_column(String, nullable=True)
    variant: Mapped[str | None] = mapped_column(String, nullable=True)
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    # Unique: prevents duplicate sends to one person and double-counted conversions.
    idempotency_key: Mapped[str] = mapped_column(String, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
