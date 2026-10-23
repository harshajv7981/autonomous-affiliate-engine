"""Register a real affiliate offer from the link your network gives you."""
from __future__ import annotations

import re

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from db.models import OfferModel

SUB_ID_PLACEHOLDER = "{sub_id}"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "offer"


def validate_affiliate_url(url: str) -> None:
    if not url.startswith("https://"):
        raise ValueError("Affiliate URL must start with https://")
    if SUB_ID_PLACEHOLDER not in url:
        raise ValueError(
            "Put {sub_id} where the network's tracking parameter goes, "
            "e.g. ...&tid={sub_id} (ClickBank) or ...&subId1={sub_id} (Impact)"
        )
    try:
        url.format(offer_id="", sub_id="")
    except (KeyError, IndexError, ValueError) as error:
        raise ValueError("The URL may only contain the {sub_id} placeholder") from error


def create_real_offer(
    session: Session,
    *,
    name: str,
    url: str,
    payout: float,
    network: str = "manual",
    external_id: str | None = None,
    geo: str = "US",
    category: str = "general",
    advertiser: str = "",
    email_allowed: bool = False,
    terms_url: str | None = None,
) -> OfferModel:
    """email_allowed must be confirmed from the program's own terms; never inferred."""
    validate_affiliate_url(url)
    if payout < 0:
        raise ValueError("payout must be >= 0")
    external = external_id or _slug(name)
    values = {
        "id": f"{_slug(network)}-{external}",
        "network_id": network,
        "external_offer_id": external,
        "name": name,
        "description": f"Real offer on {network}",
        "advertiser": advertiser or network,
        "category": category,
        "geo": geo.upper(),
        "payout": payout,
        "payout_type": "CPA",
        "epc": 0.0,
        "conversion_rate": 0.0,
        "allowed_traffic_types": ["email"] if email_allowed else [],
        "email_allowed": email_allowed,
        "email_approval_required": False,
        "terms_url": terms_url,
        "tracking_url_template": url,
        "status": "active",
        "is_simulated": False,
    }
    stmt = insert(OfferModel).values(**values)
    session.execute(stmt.on_conflict_do_update(
        constraint="uq_offers_network_external",
        set_={key: stmt.excluded[key] for key in values if key != "id"},
    ))
    session.commit()
    return session.get(OfferModel, values["id"]) or session.query(OfferModel).filter_by(
        network_id=network, external_offer_id=external
    ).one()
