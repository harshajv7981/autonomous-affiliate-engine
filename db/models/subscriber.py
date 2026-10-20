from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class SubscriberModel(Base):
    __tablename__ = "subscribers"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, index=True)
    audience_id: Mapped[str] = mapped_column(ForeignKey("audiences.id"), index=True)
    permission_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    unsubscribed: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String, default="active", index=True)
