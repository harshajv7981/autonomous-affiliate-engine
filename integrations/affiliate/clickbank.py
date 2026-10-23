"""ClickBank adapter: pulls affiliate orders from the Orders API (rest/1.3/orders2/list).

Field names follow ClickBank's published schema (GET /rest/1.3/orders2/schema):
orderData.receipt / transactionType / trackingId (the TID we put in links) / currency,
and lineItemData[].accountAmount (what the authenticated account earns) / itemNo.
"""
from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

import httpx

from integrations.affiliate.base import AffiliateNetworkAdapter

BASE_URL = "https://api.clickbank.com/rest/1.3"
MAX_PAGES = 50  # 100 orders per page


class ClickBankError(RuntimeError):
    pass


def _as_list(value: Any) -> list:
    # ClickBank's JSON returns a single object instead of a one-element list.
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def orders_to_rows(orders: list[dict]) -> list[dict]:
    """One commission row per line item, in the importer's column format."""
    rows = []
    for order in orders:
        for index, item in enumerate(_as_list(order.get("lineItemData"))):
            rows.append({
                "transaction id": f"{order.get('receipt')}:{item.get('itemNo') or index}",
                "tid": order.get("trackingId") or "",
                "commission": str(item.get("accountAmount", "")),
                "status": order.get("transactionType") or "",
                "currency": order.get("currency") or "USD",
            })
    return rows


class ClickBankAdapter(AffiliateNetworkAdapter):
    def __init__(self, api_key: str, transport: httpx.BaseTransport | None = None):
        if not api_key:
            raise ClickBankError("CLICKBANK_API_KEY is not set")
        self.api_key = api_key
        self.transport = transport

    async def sync_offers(self) -> list[dict]:
        return []  # ClickBank has no offer API for affiliates; add offers with make add-offer

    async def build_tracking_link(self, offer_id: str, sub_id: str) -> str:
        raise NotImplementedError("Use your HopLink with tid={sub_id} via make add-offer")

    async def sync_reports(self, since_timestamp):
        return []

    async def sync_conversions(self, since_timestamp: date, until: date | None = None) -> list[dict]:
        until = until or datetime.now(UTC).date()
        headers = {"Authorization": self.api_key, "Accept": "application/json"}
        params = {"startDate": since_timestamp.isoformat(), "endDate": until.isoformat(), "role": "AFFILIATE"}
        orders: list[dict] = []
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=30, transport=self.transport) as client:
            for page in range(1, MAX_PAGES + 1):
                response = await client.get("/orders2/list", params=params, headers={**headers, "Page": str(page)})
                if response.status_code == 401:
                    raise ClickBankError("ClickBank rejected the API key (401). Check CLICKBANK_API_KEY.")
                if response.status_code == 403:
                    raise ClickBankError("API key lacks the api_order_read role (403).")
                if response.status_code == 204:  # no orders in range
                    break
                response.raise_for_status()
                orders += _as_list(response.json().get("orderData"))
                if response.status_code != 206:  # 206 = more pages available
                    break
        return orders_to_rows(orders)
