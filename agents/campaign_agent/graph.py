from domain.campaigns.campaign import Campaign


def generate_creative(offer: object, audience: object) -> dict[str, str]:
    """Deterministic templated creative. AI seam: swap this for an LLM call behind
    the same signature. Output must stay clear of prohibited claims (content_rules)
    and carry a disclosure + unsubscribe reference."""
    name = getattr(offer, "name", "this offer")
    advertiser = getattr(offer, "advertiser", "our partner")
    segment = getattr(audience, "name", "subscribers")
    return {
        "subject": f"{name}: a pick for {segment}",
        "preheader": f"From {advertiser}. You can unsubscribe anytime.",
        "body": (
            f"We think {name} from {advertiser} is worth a look. "
            f"Tap below to learn more.\n\n"
            f"Affiliate disclosure: we may earn a commission. "
            f"Unsubscribe anytime using the link below."
        ),
        "cta": "Learn more",
    }


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
