"""Public endpoints reached from real test emails: click redirect, unsubscribe,
and the mock affiliate network's offer page / test conversion postback."""
import uuid
from datetime import UTC, datetime
from html import escape
from urllib.parse import quote

from app.config import settings
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from agents.campaign_agent.graph import tracking_url
from db.models import OfferModel, SubscriberModel, SuppressionRecord
from db.session import get_db
from services.event_log import click_key, find_event, record_event, sent_key

router = APIRouter(tags=["tracking"])


def _page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(
        f"<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        f"<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<title>{escape(title)}</title></head>"
        f"<body style='font-family:system-ui;max-width:560px;margin:3rem auto;padding:0 1rem'>"
        f"<h1>{escape(title)}</h1>{body}</body></html>"
    )


@router.get("/r/{campaign_id}/{subscriber_id}")
def click(campaign_id: str, subscriber_id: str, db: Session = Depends(get_db)):  # noqa: B008
    sent = find_event(db, sent_key(campaign_id, subscriber_id))
    if sent is None:
        raise HTTPException(status_code=404, detail="Unknown link")
    offer = db.get(OfferModel, sent.offer_id)
    # Short opaque per-click id: fits every network's sub-id field and is what the
    # network echoes back in its commission report.
    click_id = uuid.uuid4().hex[:16]
    url = tracking_url(offer, click_id) if offer else None
    if not url:
        raise HTTPException(status_code=404, detail="Offer unavailable")
    record_event(db, "click", campaign_id, subscriber_id=subscriber_id,
                 offer_id=sent.offer_id, variant=sent.variant, key=click_key(click_id))
    if url.startswith("/"):  # mock network is served by this API
        url = settings.public_base_url + url
    return RedirectResponse(url, status_code=302)


@router.get("/unsubscribe")
def unsubscribe_page(subscriber: str, campaign: str = "") -> HTMLResponse:
    # Confirm step: mail scanners that prefetch links must not unsubscribe people.
    action = f"/unsubscribe?subscriber={quote(subscriber)}&campaign={quote(campaign)}"
    return _page("Unsubscribe", (
        f"<p>Stop receiving these emails?</p>"
        f"<form method='post' action='{escape(action)}'><button type='submit'>Unsubscribe</button></form>"
    ))


@router.post("/unsubscribe")
def unsubscribe(subscriber: str, campaign: str = "", db: Session = Depends(get_db)) -> HTMLResponse:  # noqa: B008
    row = db.get(SubscriberModel, subscriber)
    if row is None:
        raise HTTPException(status_code=404, detail="Unknown subscriber")
    if not row.unsubscribed:
        row.unsubscribed = True
        db.add(SuppressionRecord(
            id=uuid.uuid4().hex, email=row.email, subscriber_id=row.id,
            reason="unsubscribed", created_at=datetime.now(UTC),
        ))
        db.commit()
    record_event(db, "unsubscribe", campaign or "unknown", subscriber_id=row.id, key=f"unsub:{row.id}")
    return _page("Unsubscribed", "<p>You won't receive any more emails from us.</p>")


@router.get("/mock-network/click")
def mock_offer_page(offer_id: str, sub_id: str, db: Session = Depends(get_db)) -> HTMLResponse:  # noqa: B008
    offer = db.get(OfferModel, offer_id)
    if offer is None:
        raise HTTPException(status_code=404, detail="Unknown offer")
    action = f"/mock-network/convert?offer_id={quote(offer_id)}&sub_id={quote(sub_id)}"
    return _page(offer.name, (
        f"<p><strong>Test offer page (mock affiliate network).</strong> Nothing is sold and "
        f"no money moves. Use the button to record a test conversion.</p>"
        f"<p>{escape(offer.description)}</p>"
        f"<form method='post' action='{escape(action)}'>"
        f"<button type='submit'>Complete test purchase</button></form>"
    ))


@router.post("/mock-network/convert")
def mock_conversion(offer_id: str, sub_id: str, db: Session = Depends(get_db)) -> HTMLResponse:  # noqa: B008
    click = find_event(db, click_key(sub_id))
    offer = db.get(OfferModel, offer_id)
    if click is None or offer is None or click.offer_id != offer_id or not offer.is_simulated:
        raise HTTPException(status_code=404, detail="No matching click for this mock offer")
    recorded = record_event(
        db, "conversion", click.campaign_id, subscriber_id=click.subscriber_id, offer_id=offer_id,
        variant=click.variant, amount=offer.payout, key=f"conversion:{sub_id}",
    )
    message = "Test conversion recorded." if recorded else "Already recorded — counted once."
    return _page("Thanks", f"<p>{message} (test commission ${offer.payout:.2f}, not real money)</p>")
