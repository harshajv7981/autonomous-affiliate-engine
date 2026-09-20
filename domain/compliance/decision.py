from dataclasses import dataclass
from enum import Enum


class ComplianceDecision(str, Enum):
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class ComplianceResult:
    decision: ComplianceDecision
    reasons: tuple[str, ...]
    evaluated_rules: tuple[str, ...]

    @property
    def is_sendable(self) -> bool:
        return self.decision is ComplianceDecision.APPROVE
