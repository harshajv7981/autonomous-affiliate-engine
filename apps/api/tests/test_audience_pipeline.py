from domain.audiences.audience import Audience
from policies.audience_rules import check_audience_eligibility


def test_audience_eligible_when_permission_verified():
    audience = Audience(
        id="aud-1",
        name="Approved Audience",
        source_type="email",
        source_provider="mock",
        geo="US",
        category="finance",
        estimated_size=10000,
        permission_model="explicit_opt_in",
        permission_verified=True,
        email_allowed=True,
        status="active",
    )

    result = check_audience_eligibility(audience, "email")

    assert result["eligible"] is True
    assert result["reason"] is None


def test_audience_ineligible_when_permission_missing():
    audience = Audience(
        id="aud-2",
        name="Unverified Audience",
        source_type="email",
        source_provider="mock",
        geo="US",
        category="finance",
        estimated_size=10000,
        permission_model="explicit_opt_in",
        permission_verified=False,
        email_allowed=True,
        status="active",
    )

    result = check_audience_eligibility(audience, "email")

    assert result["eligible"] is False
    assert result["reason"] == "Audience permission is not verified"
