from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class ConsentRecord(Base):
    __tablename__ = "consent_records"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    subscriber_id: Mapped[str] = mapped_column(ForeignKey("subscribers.id"), index=True)
    source: Mapped[str] = mapped_column(String)
    consent_model: Mapped[str] = mapped_column(String)
    consented_at: Mapped[datetime] = mapped_column(DateTime)
