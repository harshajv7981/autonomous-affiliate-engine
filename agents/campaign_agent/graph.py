from domain.campaigns.campaign import Campaign


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
