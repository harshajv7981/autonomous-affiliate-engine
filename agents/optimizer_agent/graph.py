"""Optimizer agent: rule-based decisions on campaign performance.

Runs in recommendation-only mode: decisions are reported, never auto-applied,
until several real campaigns have reliable data. It can never override the
compliance gate. AI seam: a later version may propose ideas, but the action
stays bounded by these rules.
"""
from __future__ import annotations

# Allowed actions: SCALE, PAUSE, KILL, TEST, REDUCE, RETRY
SCALE_CVR_THRESHOLD = 0.03
# Mailbox providers start suspending senders around a 0.1% complaint rate.
MAX_COMPLAINT_RATE = 0.001
MAX_UNSUBSCRIBE_RATE = 0.005
MODE = "recommendation"


def decide(metrics: dict, net_contribution: float) -> dict:
    cvr = float(metrics.get("cvr", 0.0))
    conversions = int(metrics.get("conversions", 0))
    clicks = int(metrics.get("clicks", 0))

    if clicks == 0:
        action, reason = "RETRY", "NO_CLICKS_RECORDED"
    elif float(metrics.get("complaint_rate", 0.0)) >= MAX_COMPLAINT_RATE:
        action, reason = "PAUSE", "COMPLAINT_RATE_HIGH"
    elif conversions == 0:
        action, reason = "KILL", "NO_CONVERSIONS_NEGATIVE_CONTRIBUTION"
    elif net_contribution < 0:
        action, reason = "PAUSE", "NEGATIVE_CONTRIBUTION"
    elif float(metrics.get("unsubscribe_rate", 0.0)) >= MAX_UNSUBSCRIBE_RATE:
        action, reason = "REDUCE", "UNSUBSCRIBE_RATE_HIGH"
    elif cvr >= SCALE_CVR_THRESHOLD:
        action, reason = "SCALE", "STRONG_CVR_POSITIVE_CONTRIBUTION"
    else:
        action, reason = "TEST", "POSITIVE_BUT_UNPROVEN"

    return {
        "action": action,
        "reason": reason,
        "net_contribution": round(net_contribution, 2),
        "mode": MODE,
        "applied": False,
    }
