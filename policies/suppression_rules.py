def check_recipient_eligibility(recipient: object) -> dict:
    if getattr(recipient, "status", "") != "active":
        return {"eligible": False, "reason": "Recipient is not active"}
    if getattr(recipient, "unsubscribed", False):
        return {"eligible": False, "reason": "Recipient is unsubscribed"}
    if not getattr(recipient, "permission_verified", False):
        return {"eligible": False, "reason": "Recipient permission is not verified"}
    return {"eligible": True, "reason": None}
