def score_offer(offer: object) -> dict[str, object]:
    epc_score = min((getattr(offer, "epc", 0.0) / 100.0), 1.0)
    cvr_score = min((getattr(offer, "conversion_rate", 0.0) * 100.0), 1.0)
    score = round((epc_score * 0.3) + (cvr_score * 0.2) + 0.5, 3)
    return {
        "offer_id": getattr(offer, "id", "unknown"),
        "score": score,
        "recommended_action": "TEST" if score >= 0.7 else "REVIEW",
    }
