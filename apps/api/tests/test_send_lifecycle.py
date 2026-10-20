import pytest

from domain.campaigns.campaign import Campaign
from domain.compliance import ComplianceDecision, ComplianceResult
from domain.recipients.recipient import Recipient
from policies.suppression_rules import check_recipient_eligibility
from services.campaign_execution import calculate_revenue, execute_campaign, register_click


def test_recipient_suppression_blocks_unsubscribed_or_unverified_users():
    recipient = Recipient(
        id="r-1",
        email="user@example.com",
        audience_id="aud-1",
        permission_verified=True,
        unsubscribed=False,
        status="active",
    )
    unsubscribed = Recipient(
        id="r-2",
        email="unsubscribed@example.com",
        audience_id="aud-1",
        permission_verified=True,
        unsubscribed=True,
        status="active",
    )
    unverified = Recipient(
        id="r-3",
        email="unverified@example.com",
        audience_id="aud-1",
        permission_verified=False,
        unsubscribed=False,
        status="active",
    )

    assert check_recipient_eligibility(recipient).is_sendable is True
    assert check_recipient_eligibility(unsubscribed).is_sendable is False
    assert check_recipient_eligibility(unverified).is_sendable is False


def test_mock_send_pipeline_tracks_clicks_and_revenue():
    campaign = Campaign(
        id="camp-1",
        offer_id="offer-1",
        audience_id="aud-1",
        name="Test Campaign",
        state="SCHEDULED",
        subject_line="Launch update",
        body="Learn more now",
        cta="Learn more",
    )
    recipients = [
        Recipient("r-1", "a@example.com", "aud-1", True, False, "active"),
        Recipient("r-2", "b@example.com", "aud-1", True, False, "active"),
        Recipient("r-3", "c@example.com", "aud-1", True, True, "active"),
        Recipient("r-4", "d@example.com", "aud-other", True, False, "active"),
    ]

    approved = ComplianceResult(ComplianceDecision.APPROVE, (), ())
    result = execute_campaign(campaign, recipients, approved)
    click = register_click(campaign.id, "r-1")
    revenue = calculate_revenue(conversions=2, payout_per_conversion=25.0)

    assert result["sent_count"] == 2
    assert click["click_id"].startswith("click-")
    assert click["click_id"] != register_click("camp-other", "r-1")["click_id"]
    assert revenue == 50.0


def test_campaign_cannot_send_unless_compliance_approves():
    campaign = Campaign(id="camp-2", offer_id="offer-1", audience_id="aud-1", name="Draft")
    recipient = Recipient("r-1", "a@example.com", "aud-1", True, False, "active")

    for decision in (ComplianceDecision.BLOCK, ComplianceDecision.REVIEW):
        with pytest.raises(ValueError, match="not approved"):
            execute_campaign(campaign, [recipient], ComplianceResult(decision, ("X",), ()))
    assert campaign.state == "DRAFT"
