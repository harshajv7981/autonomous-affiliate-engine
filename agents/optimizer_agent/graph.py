"""Optimizer agent: rule-based decisions on campaign performance.

Decisions are deterministic (PROJECT_INSTRUCTIONS section 19). This is an AI seam:
a later version can ask an LLM for ideas, but the chosen action stays bounded by
these rules so the optimizer can never override hard compliance/eligibility.
"""
from __future__ import annotations

# Allowed actions: SCALE, PAUSE, KILL, TEST, REDUCE, RETRY
SCALE_CVR_THRESHOLD = 0.03


def decide(metrics: dict, net_contribution: float) -> dict:
    cvr = float(metrics.get("cvr", 0.0))
    conversions = int(metrics.get("conversions", 0))
    clicks = int(metrics.get("clicks", 0))

    if clicks == 0:
        action, reason = "RETRY", "NO_CLICKS_RECORDED"
    elif conversions == 0:
        action, reason = "KILL", "NO_CONVERSIONS_NEGATIVE_CONTRIBUTION"
    elif net_contribution < 0:
        action, reason = "PAUSE", "NEGATIVE_CONTRIBUTION"
    elif cvr >= SCALE_CVR_THRESHOLD:
        action, reason = "SCALE", "STRONG_CVR_POSITIVE_CONTRIBUTION"
    else:
        action, reason = "TEST", "POSITIVE_BUT_UNPROVEN"

    return {"action": action, "reason": reason, "net_contribution": round(net_contribution, 2)}
