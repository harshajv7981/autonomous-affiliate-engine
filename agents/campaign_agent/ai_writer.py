"""AI copywriter using a local Ollama model ($0). AI drafts; code stays in charge:

- the model writes only subjects, preheader, body and CTA;
- disclosure, unsubscribe text and every link are added by code, never by the model;
- output is validated (length, no URLs, prohibited-claim rules) and anything invalid,
  or any Ollama failure, falls back to the deterministic template;
- the send compliance gate still checks the final package.
"""
from __future__ import annotations

import json
import re

import httpx
from app.config import settings

from agents.campaign_agent.graph import generate_creative
from policies.content_rules import check_content_compliance

LIMITS = {"subject_a": 80, "subject_b": 80, "preheader": 120, "body": 700, "cta": 30}
SCHEMA = {
    "type": "object",
    "properties": {field: {"type": "string"} for field in LIMITS},
    "required": list(LIMITS),
}
LINK_PATTERN = re.compile(r"https?://|www\.|\.com\b", re.IGNORECASE)


def build_prompt(offer: object, audience: object) -> str:
    return (
        "Write a short, honest affiliate email.\n"
        f"Product: {getattr(offer, 'name', '')}\n"
        f"Brand: {getattr(offer, 'advertiser', '')}\n"
        f"About: {getattr(offer, 'description', '')}\n"
        f"Readers: people interested in {getattr(offer, 'category', 'this topic')}\n\n"
        "Return JSON with: subject_a and subject_b (two different angles, under 60 characters), "
        "preheader (under 90 characters), body (2-4 plain sentences), cta (under 4 words).\n"
        "Rules: no links or URLs, no prices or discounts, no guarantees, no income or health "
        "claims, no fake urgency or scarcity, do not invent features. Do not mention "
        "unsubscribing or affiliate disclosure; those are added automatically."
    )


def write_copy(offer: object, audience: object, client: httpx.Client | None = None) -> dict | None:
    """Validated AI copy, or None if the model is unavailable or the copy is unusable."""
    owns_client = client is None
    client = client or httpx.Client(timeout=settings.llm_timeout_seconds)
    try:
        response = client.post(f"{settings.ollama_url}/api/generate", json={
            "model": settings.llm_model,
            "prompt": build_prompt(offer, audience),
            "format": SCHEMA,
            "stream": False,
            "think": False,
            "options": {"temperature": 0.7},
        })
        response.raise_for_status()
        data = json.loads(response.json()["response"])
    except (httpx.HTTPError, KeyError, ValueError, TypeError):
        return None
    finally:
        if owns_client:
            client.close()

    if not isinstance(data, dict):
        return None
    copy = {field: str(data.get(field) or "").strip() for field in LIMITS}
    if any(not value or len(value) > LIMITS[field] for field, value in copy.items()):
        return None
    if any(LINK_PATTERN.search(value) for value in copy.values()):
        return None  # links are always ours
    headline = f"{copy['subject_a']} {copy['subject_b']} {copy['preheader']} {copy['cta']}"
    if not check_content_compliance(headline, copy["body"]).is_sendable:
        return None
    return copy


def creative_for_send(offer: object, audience: object, client: httpx.Client | None = None) -> dict:
    """AI copy when enabled and valid; otherwise the deterministic template."""
    template = generate_creative(offer, audience)
    if settings.llm_provider != "ollama":
        return {**template, "copy_source": "template"}
    copy = write_copy(offer, audience, client)
    if copy is None:
        return {**template, "copy_source": "template_fallback"}
    return {
        "subject": copy["subject_a"],
        "subject_variants": [copy["subject_a"], copy["subject_b"]],
        "preheader": copy["preheader"],
        "body": f"{copy['body']}\n\n{template['disclosure']} Unsubscribe anytime using the link below.",
        "cta": copy["cta"],
        "disclosure": template["disclosure"],
        "copy_source": f"ai:{settings.llm_model}",
    }
