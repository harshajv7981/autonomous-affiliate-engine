from domain.campaigns.campaign import Campaign


def generate_creative(offer: object, audience: object) -> dict[str, str]:
    """Deterministic templated creative. AI seam: swap this for an LLM call behind
    the same signature. Output must stay clear of prohibited claims (content_rules)
    and carry a disclosure + unsubscribe reference."""
    name = getattr(offer, "name", "this offer")
    advertiser = getattr(offer, "advertiser", "our partner")
    segment = getattr(audience, "name", "subscribers")
    disclosure = "Affiliate disclosure: we may earn a commission if you buy through this link."
    subject = f"{name}: a pick for {segment}"
    return {
        "subject": subject,
        # A/B variants for testing; every variant goes through the compliance gate.
        "subject_variants": [subject, f"Worth a look: {name} from {advertiser}"],
        "preheader": f"From {advertiser}. You can unsubscribe anytime.",
        "body": (
            f"We think {name} from {advertiser} is worth a look. "
            f"Tap below to learn more.\n\n"
            f"{disclosure} "
            f"Unsubscribe anytime using the link below."
        ),
        "cta": "Learn more",
        "disclosure": disclosure,
    }


def tracking_url(offer: object, sub_id: str) -> str | None:
    """Affiliate tracking link with our sub_id so network conversions map back to a campaign."""
    template = getattr(offer, "tracking_url_template", None)
    return template.format(offer_id=getattr(offer, "id", ""), sub_id=sub_id) if template else None


def build_campaign(offer: object, audience: object, subject_line: str, preheader: str, body: str, cta: str) -> Campaign:
    return Campaign(
        id=f"campaign-{getattr(offer, 'id', 'unknown')}-{getattr(audience, 'id', 'audience')}",
        offer_id=getattr(offer, 'id', 'unknown'),
        audience_id=getattr(audience, 'id', 'audience'),
        name=f"{getattr(offer, 'name', 'Offer')} campaign",
        state="GENERATING",
        subject_line=subject_line,
        preheader=preheader,
        body=body,
        cta=cta,
        approved=False,
        metadata={
            "offer_name": getattr(offer, "name", "unknown"),
            "audience_name": getattr(audience, "name", "unknown"),
        },
    )
