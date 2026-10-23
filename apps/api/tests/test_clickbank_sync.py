import asyncio
import json
from datetime import date

import httpx
import pytest
from app.config import settings

from integrations.affiliate.clickbank import ClickBankAdapter, ClickBankError, orders_to_rows
from services.network_sync import sync_clickbank

ORDER_1 = {"receipt": "R1", "transactionType": "SALE", "trackingId": "abc123", "currency": "USD",
           "lineItemData": [{"itemNo": "1", "accountAmount": 30.5}, {"itemNo": "2", "accountAmount": 10}]}
ORDER_2 = {"receipt": "R2", "transactionType": "RFND", "trackingId": "abc123", "currency": "USD",
           "lineItemData": {"itemNo": "1", "accountAmount": -30.5}}  # single object, not a list


def _transport(calls, pages):
    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        page = int(request.headers["Page"])
        status = 206 if page < len(pages) else 200
        return httpx.Response(status, content=json.dumps({"orderData": pages[page - 1]}))
    return httpx.MockTransport(handler)


def test_paginates_and_sends_key_and_affiliate_role():
    calls = []
    adapter = ClickBankAdapter("API-KEY", transport=_transport(calls, [[ORDER_1], ORDER_2]))
    rows = asyncio.run(adapter.sync_conversions(date(2026, 1, 1), date(2026, 1, 31)))

    assert len(calls) == 2
    assert calls[0].headers["Authorization"] == "API-KEY"
    assert calls[0].url.params["role"] == "AFFILIATE"
    assert calls[0].url.params["startDate"] == "2026-01-01"
    assert [r["transaction id"] for r in rows] == ["R1:1", "R1:2", "R2:1"]


def test_bad_key_gives_clear_error():
    transport = httpx.MockTransport(lambda request: httpx.Response(401, text="No API key provided"))
    with pytest.raises(ClickBankError, match="rejected the API key"):
        asyncio.run(ClickBankAdapter("bad", transport=transport).sync_conversions(date(2026, 1, 1)))


def test_missing_key_refused_before_any_request():
    with pytest.raises(ClickBankError, match="not set"):
        ClickBankAdapter("")


def test_no_orders_returns_empty():
    transport = httpx.MockTransport(lambda request: httpx.Response(204))
    assert asyncio.run(ClickBankAdapter("k", transport=transport).sync_conversions(date(2026, 1, 1))) == []


def test_sync_imports_and_nets_refund(fresh_db, monkeypatch):
    monkeypatch.setattr(settings, "clickbank_api_key", "API-KEY")
    result = asyncio.run(sync_clickbank(fresh_db, transport=_transport([], [[ORDER_1, ORDER_2]])))
    assert result["rows"] == 3 and result["invalid"] == 0

    from db.models import CommissionModel
    from services.commission_import import summarize
    earnings = summarize(fresh_db.query(CommissionModel).all())[0]
    assert earnings["confirmed"] == 10.0  # 30.50 + 10.00 - 30.50 refund
    assert earnings["reversed"] == 30.5


def test_orders_to_rows_handles_empty_line_items():
    assert orders_to_rows([{"receipt": "R9", "transactionType": "SALE"}]) == []
