def check_audience_eligibility(audience: object, traffic_type: str) -> dict:
    if getattr(audience, "status", "") != "active":
        return {"eligible": False, "reason": "Audience is not active"}
    if traffic_type == "email" and not getattr(audience, "email_allowed", False):
        return {"eligible": False, "reason": "Email traffic is not allowed for this audience"}
    if not getattr(audience, "permission_verified", False):
        return {"eligible": False, "reason": "Audience permission is not verified"}
    return {"eligible": True, "reason": None}
