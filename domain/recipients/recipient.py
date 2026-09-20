from dataclasses import dataclass


@dataclass
class Recipient:
    id: str
    email: str
    audience_id: str
    permission_verified: bool = True
    unsubscribed: bool = False
    status: str = "active"
