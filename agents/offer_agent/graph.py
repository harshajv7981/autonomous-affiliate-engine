# shortcut: fixed $20 EPC / 5% CVR ceilings; switch to ranking against real offer data once it exists.
EPC_CEILING = 20.0
CVR_CEILING = 0.05


def score_offer(offer: object) -> dict[str, object]:
    epc_score = min(getattr(offer, "epc", 0.0) / EPC_CEILING, 1.0)
    cvr_score = min(getattr(offer, "conversion_rate", 0.0) / CVR_CEILING, 1.0)
    score = round((epc_score * 0.5) + (cvr_score * 0.5), 3)
    return {
        "offer_id": getattr(offer, "id", "unknown"),
        "score": score,
        "recommended_action": "TEST" if score >= 0.7 else "REVIEW",
    }
