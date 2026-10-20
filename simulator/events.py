"""Deterministic event simulator: turns a send into a delivery/click/conversion
funnel and commission, with no randomness so economics are reproducible.

Rates are configurable per PROJECT_INSTRUCTIONS section 16. Per-offer
conversion_rate drives the variety the optimizer needs to make real decisions.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationRates:
    delivery_rate: float = 0.97
    open_rate: float = 0.30
    click_rate: float = 0.08  # of delivered


def simulate_campaign_outcome(sent_count: int, offer: object, rates: SimulationRates | None = None) -> dict:
    """Expected-value funnel. conversions use the offer's own conversion_rate so
    different offers produce different contribution, feeding the optimizer."""
    rates = rates or SimulationRates()
    delivered = int(sent_count * rates.delivery_rate)
    opens = int(delivered * rates.open_rate)
    clicks = int(delivered * rates.click_rate)
    conversion_rate = float(getattr(offer, "conversion_rate", 0.0))
    conversions = int(clicks * conversion_rate)
    commission = conversions * float(getattr(offer, "payout", 0.0))
    return {
        "sent": sent_count,
        "delivered": delivered,
        "opens": opens,
        "clicks": clicks,
        "conversions": conversions,
        "commission": round(commission, 2),
    }
