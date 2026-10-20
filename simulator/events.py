"""Deterministic event simulator: turns a send into a delivery/bounce/open/click/
conversion/unsubscribe/complaint funnel and commission, with no randomness so
economics are reproducible.

Every result is marked is_simulated=True. Simulated revenue is engineering data
only and must never be mixed with or reported as real affiliate earnings.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationRates:
    delivery_rate: float = 0.97  # the rest bounce
    open_rate: float = 0.30
    click_rate: float = 0.08  # of delivered
    unsubscribe_rate: float = 0.002  # of delivered
    complaint_rate: float = 0.0005  # of delivered


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
        "bounces": sent_count - delivered,
        "opens": opens,
        "clicks": clicks,
        "conversions": conversions,
        "unsubscribes": int(delivered * rates.unsubscribe_rate),
        "complaints": int(delivered * rates.complaint_rate),
        "commission": round(commission, 2),
        "is_simulated": True,
    }
