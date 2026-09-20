from domain.campaigns.campaign import Campaign
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

    assert check_recipient_eligibility(recipient)["eligible"] is True
    assert check_recipient_eligibility(unsubscribed)["eligible"] is False
    assert check_recipient_eligibility(unverified)["eligible"] is False


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
    ]

    result = execute_campaign(campaign, recipients)
    click = register_click(campaign.id, "r-1")
    revenue = calculate_revenue(2, 25.0)

    assert result["sent_count"] == 2
    assert click["click_id"].startswith("click-")
    assert revenue == 50.0
