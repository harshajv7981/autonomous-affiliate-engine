"""Import real commissions from any network's CSV report and attribute them to clicks.

Column names are auto-detected (case-insensitive) and can be overridden. Statuses
are normalized to PENDING/APPROVED/REJECTED/REVERSED/PAID; unknown -> PENDING so
nothing is counted as confirmed money by mistake.
"""
from __future__ import annotations

import uuid
from collections.abc import Iterable
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from db.models import CommissionModel
from services.event_log import click_key, find_event

CANDIDATES = {
    "external_id": ("transaction id", "transaction_id", "receipt", "order id", "order_id", "action id", "id"),
    "sub_id": ("sub_id", "subid", "sub id", "subid1", "sub_id1", "tid", "tracking id", "tracking_id", "cam"),
    "amount": ("commission", "commission amount", "earnings", "payout", "amount"),
    "status": ("status", "state", "transaction type", "type"),
    "currency": ("currency", "currency code"),
}
STATUS_WORDS = {
    "APPROVED": ("approved", "approve", "locked", "sale", "bill", "completed", "confirmed"),
    "PAID": ("paid",),
    "PENDING": ("pending", "open", "new", "waiting"),
    "REVERSED": ("reversed", "refund", "rfnd", "chargeback", "cgbk", "returned", "clawback"),
    "REJECTED": ("rejected", "declined", "cancelled", "canceled", "void", "invalid"),
}
CONFIRMED = ("APPROVED", "PAID")


def normalize_status(raw: str | None) -> str:
    text = (raw or "").strip().lower()
    for status, words in STATUS_WORDS.items():
        if text in words:
            return status
    return "PENDING"


def parse_amount(raw: str | None) -> Decimal:
    cleaned = (raw or "").replace("$", "").replace(",", "").replace("€", "").replace("£", "").strip()
    return Decimal(cleaned).quantize(Decimal("0.01"))


def detect_columns(headers: Iterable[str], overrides: dict[str, str] | None = None) -> dict[str, str]:
    by_lower = {header.strip().lower(): header for header in headers}
    columns = {}
    for field, names in CANDIDATES.items():
        override = (overrides or {}).get(field)
        if override:
            if override.strip().lower() not in by_lower:
                raise ValueError(f"Column '{override}' not found in report")
            columns[field] = by_lower[override.strip().lower()]
            continue
        match = next((by_lower[name] for name in names if name in by_lower), None)
        if match:
            columns[field] = match
    missing = [field for field in ("external_id", "sub_id", "amount") if field not in columns]
    if missing:
        raise ValueError(f"Could not find columns for {missing}; pass them explicitly")
    return columns


def import_commissions(
    session: Session, rows: list[dict], network: str, overrides: dict[str, str] | None = None,
) -> dict:
    if not rows:
        return {"rows": 0, "attributed": 0, "unattributed": 0, "invalid": 0}
    columns = detect_columns(rows[0].keys(), overrides)
    now = datetime.now(UTC)
    counts = {"rows": len(rows), "attributed": 0, "unattributed": 0, "invalid": 0}

    for row in rows:
        external_id = (row.get(columns["external_id"]) or "").strip()
        try:
            amount = parse_amount(row.get(columns["amount"]))
        except InvalidOperation:
            amount = None
        if not external_id or amount is None:
            counts["invalid"] += 1
            continue
        status = normalize_status(row.get(columns["status"])) if "status" in columns else "PENDING"
        if amount < 0:
            # Refund/chargeback reported as its own negative row: keep the original sale
            # row intact and net the reversal against it.
            status, external_id = "REVERSED", f"{external_id}:reversal"

        click_id = (row.get(columns["sub_id"]) or "").strip() or None
        click = find_event(session, click_key(click_id)) if click_id else None
        counts["attributed" if click else "unattributed"] += 1

        values = {
            "id": uuid.uuid4().hex,
            "network": network,
            "external_id": external_id,
            "click_id": click_id,
            "campaign_id": click.campaign_id if click else None,
            "subscriber_id": click.subscriber_id if click else None,
            "offer_id": click.offer_id if click else None,
            "amount": amount,
            "currency": ((row.get(columns["currency"]) or "") if "currency" in columns else "").strip().upper() or "USD",
            "status": status,
            "is_simulated": False,
            "imported_at": now,
            "updated_at": now,
        }
        stmt = insert(CommissionModel).values(**values)
        # Re-importing a report updates status/amount in place (e.g. PENDING -> APPROVED -> PAID).
        session.execute(stmt.on_conflict_do_update(
            constraint="uq_commissions_network_external",
            set_={key: stmt.excluded[key] for key in
                  ("click_id", "campaign_id", "subscriber_id", "offer_id", "amount", "currency", "status", "updated_at")},
        ))
    session.commit()
    return counts


def summarize(commissions: Iterable[CommissionModel]) -> list[dict]:
    """Per-currency totals. Confirmed = approved + paid, minus netted reversal rows."""
    totals: dict[str, dict[str, Decimal | int]] = {}
    for commission in commissions:
        bucket = totals.setdefault(commission.currency, {
            "confirmed": Decimal(0), "pending": Decimal(0), "paid": Decimal(0),
            "reversed": Decimal(0), "attributed": 0, "unattributed": 0,
        })
        bucket["attributed" if commission.campaign_id else "unattributed"] += 1
        if commission.status in CONFIRMED:
            bucket["confirmed"] += commission.amount
        if commission.status == "PAID":
            bucket["paid"] += commission.amount
        elif commission.status == "PENDING":
            bucket["pending"] += commission.amount
        elif commission.status == "REVERSED":
            bucket["reversed"] += abs(commission.amount)
            if commission.amount < 0:
                bucket["confirmed"] += commission.amount
    return [
        {"currency": currency, **{k: float(v) if isinstance(v, Decimal) else v for k, v in bucket.items()}}
        for currency, bucket in sorted(totals.items())
    ]
