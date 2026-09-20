from datetime import datetime, timezone

from domain.compliance.decision import ComplianceDecision, ComplianceResult
from domain.events.event import DomainEvent, EventType
from integrations.affiliate.base import AffiliateNetworkAdapter


def test_domain_event_has_idempotent_identity_and_audit_fields():
    event = DomainEvent(
        event_id="event-1",
        event_type=EventType.CLICK_RECORDED,
        aggregate_id="campaign-1",
        occurred_at=datetime.now(timezone.utc),
        payload={"recipient_id": "recipient-1"},
    )

    assert event.event_id == "event-1"
    assert event.event_type is EventType.CLICK_RECORDED
    assert event.aggregate_id == "campaign-1"
    assert event.payload["recipient_id"] == "recipient-1"


def test_blocked_compliance_result_cannot_be_approved():
    result = ComplianceResult(
        decision=ComplianceDecision.BLOCK,
        reasons=("EMAIL_NOT_ALLOWED",),
        evaluated_rules=("offer.email_allowed",),
    )

    assert result.is_sendable is False
    assert result.decision is ComplianceDecision.BLOCK


def test_affiliate_adapter_contract_exposes_required_operations():
    required_methods = {
        "sync_offers",
        "build_tracking_link",
        "sync_conversions",
        "sync_reports",
    }

    assert required_methods.issubset(set(dir(AffiliateNetworkAdapter)))
