from domain.offers.offer import Offer


class OfferIngestionService:
    @staticmethod
    def normalize_offer(raw_offer: dict) -> Offer:
        return Offer(
            id=raw_offer["id"],
            network_id=raw_offer.get("network_id", "unknown"),
            external_offer_id=raw_offer.get("external_offer_id", raw_offer["id"]),
            name=raw_offer.get("name", "Unnamed Offer"),
            description=raw_offer.get("description", ""),
            advertiser=raw_offer.get("advertiser", "Unknown"),
            category=raw_offer.get("category", "unknown"),
            geo=raw_offer.get("geo", "US"),
            payout=float(raw_offer.get("payout", 0.0)),
            payout_type=raw_offer.get("payout_type", "CPA"),
            epc=float(raw_offer.get("epc", 0.0)),
            conversion_rate=float(raw_offer.get("conversion_rate", 0.0)),
            allowed_traffic_types=list(raw_offer.get("allowed_traffic_types", [])),
            email_allowed=bool(raw_offer.get("email_allowed", False)),
            email_approval_required=bool(raw_offer.get("email_approval_required", False)),
            terms_url=raw_offer.get("terms_url"),
            tracking_url_template=raw_offer.get("tracking_url_template"),
            status=raw_offer.get("status", "active"),
        )
