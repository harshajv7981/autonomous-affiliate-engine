from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Numeric, String, UniqueConstraint, false
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class CommissionModel(Base):
    """Real commissions as reported by the affiliate network (the source of truth for money)."""

    __tablename__ = "commissions"
    __table_args__ = (
        UniqueConstraint("network", "external_id", name="uq_commissions_network_external"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    network: Mapped[str] = mapped_column(String)
    external_id: Mapped[str] = mapped_column(String)
    click_id: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    campaign_id: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    subscriber_id: Mapped[str | None] = mapped_column(String, nullable=True)
    offer_id: Mapped[str | None] = mapped_column(String, nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))  # exact money, never float
    currency: Mapped[str] = mapped_column(String, default="USD")
    status: Mapped[str] = mapped_column(String, index=True)  # PENDING/APPROVED/REJECTED/REVERSED/PAID
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
