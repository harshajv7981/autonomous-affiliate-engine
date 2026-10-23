from __future__ import annotations

from sqlalchemy import Boolean, Integer, String, true
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class AudienceModel(Base):
    __tablename__ = "audiences"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    source_type: Mapped[str] = mapped_column(String)
    source_provider: Mapped[str] = mapped_column(String)
    geo: Mapped[str] = mapped_column(String, index=True)
    category: Mapped[str] = mapped_column(String, index=True)
    estimated_size: Mapped[int] = mapped_column(Integer, default=0)
    permission_model: Mapped[str] = mapped_column(String)
    permission_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String, default="active", index=True)
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
