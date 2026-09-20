from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Campaign:
    id: str
    offer_id: str
    audience_id: str
    name: str
    state: str = "DRAFT"
    subject_line: Optional[str] = None
    preheader: Optional[str] = None
    body: Optional[str] = None
    cta: Optional[str] = None
    approved: bool = False
    metadata: dict = field(default_factory=dict)
