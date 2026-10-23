import json
from types import SimpleNamespace

import httpx
import pytest
from app.config import settings

from agents.campaign_agent.ai_writer import creative_for_send
from domain.compliance import ComplianceDecision
from policies.send_rules import validate_send

OFFER = SimpleNamespace(id="o-1", name="Focus Planner", advertiser="Acme", description="A planner",
                        category="productivity", status="active", email_allowed=True,
                        allowed_traffic_types=["email"], email_approval_required=False, geo="US")
AUDIENCE = SimpleNamespace(id="a-1", name="Readers", status="active", email_allowed=True,
                           permission_verified=True, geo="US")
GOOD = {"subject_a": "A calmer way to plan", "subject_b": "Meet Focus Planner",
        "preheader": "A simple planner from Acme.", "body": "It keeps your day simple.", "cta": "Take a look"}


def _client(payload=None, status=200, raise_error=None, seen=None):
    def handler(request):
        if seen is not None:
            seen.append(json.loads(request.content))
        if raise_error:
            raise raise_error
        return httpx.Response(status, json={"response": json.dumps(payload) if payload is not None else "not json"})
    return httpx.Client(transport=httpx.MockTransport(handler))


@pytest.fixture(autouse=True)
def ollama_on(monkeypatch):
    monkeypatch.setattr(settings, "llm_provider", "ollama")


def test_valid_ai_copy_is_used_with_code_added_disclosure_and_passes_gate():
    seen = []
    creative = creative_for_send(OFFER, AUDIENCE, _client(GOOD, seen=seen))

    assert creative["copy_source"].startswith("ai:")
    assert creative["subject_variants"] == ["A calmer way to plan", "Meet Focus Planner"]
    assert "Affiliate disclosure" in creative["body"] and "Unsubscribe" in creative["body"]
    assert seen[0]["think"] is False and seen[0]["format"]["required"]

    package = {**creative, "tracking_url": "https://t", "unsubscribe_url": "https://u",
               "sender_identity": "Lab <l@x>, 1 Main St"}
    result = validate_send(OFFER, AUDIENCE, package, already_sent=False, audience_sends=0, frequency_cap=1)
    assert result.decision is ComplianceDecision.APPROVE


@pytest.mark.parametrize("bad", [
    {**GOOD, "subject_a": "Guaranteed income starts today"},   # prohibited claim
    {**GOOD, "body": "Buy at https://evil.example now"},       # model tried to add a link
    {**GOOD, "body": "x" * 800},                                # too long
    {**GOOD, "cta": ""},                                        # missing field
])
def test_unsafe_or_invalid_ai_copy_falls_back_to_template(bad):
    creative = creative_for_send(OFFER, AUDIENCE, _client(bad))
    assert creative["copy_source"] == "template_fallback"
    assert creative["subject"] == "Focus Planner: a pick for Readers"


@pytest.mark.parametrize("client_args", [
    {"payload": None},                                          # malformed JSON
    {"payload": GOOD, "status": 500},                           # server error
    {"raise_error": httpx.ConnectError("ollama down")},         # not running
])
def test_ollama_failures_fall_back_to_template(client_args):
    assert creative_for_send(OFFER, AUDIENCE, _client(**client_args))["copy_source"] == "template_fallback"


def test_provider_none_never_calls_the_model(monkeypatch):
    monkeypatch.setattr(settings, "llm_provider", "none")
    creative = creative_for_send(OFFER, AUDIENCE, _client(raise_error=AssertionError("must not call")))
    assert creative["copy_source"] == "template"
