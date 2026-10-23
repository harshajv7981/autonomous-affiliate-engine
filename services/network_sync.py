"""Pull commissions straight from a network API into the commissions ledger."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.config import settings
from sqlalchemy.orm import Session

from integrations.affiliate.clickbank import ClickBankAdapter
from services.commission_import import import_commissions

ROW_COLUMNS = {
    "external_id": "transaction id", "sub_id": "tid", "amount": "commission",
    "status": "status", "currency": "currency",
}


async def sync_clickbank(session: Session, days: int = 30, transport=None) -> dict:
    adapter = ClickBankAdapter(settings.clickbank_api_key, transport=transport)
    rows = await adapter.sync_conversions(datetime.now(UTC).date() - timedelta(days=days))
    return import_commissions(session, rows, "clickbank", ROW_COLUMNS)
