from dataclasses import dataclass


@dataclass
class Audience:
    id: str
    name: str
    source_type: str
    source_provider: str
    geo: str
    category: str
    estimated_size: int
    permission_model: str
    permission_verified: bool = False
    email_allowed: bool = False
    status: str = "active"
