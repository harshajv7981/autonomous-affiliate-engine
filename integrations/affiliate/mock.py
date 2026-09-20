from __future__ import annotations

from typing import Any


class MockAffiliateAdapter:
    async def sync_offers(self) -> list[dict[str, Any]]:
        offers: list[dict[str, Any]] = []
        for i in range(1, 101):
            email_allowed = i % 3 != 0
            traffic_types = ["email", "social"] if email_allowed else ["social"]
            offers.append(
                {
                    "id": f"mock-offer-{i}",
                    "network_id": "mock",
                    "external_offer_id": f"ext-{i}",
                    "name": f"Mock Offer {i}",
                    "description": f"Synthetic offer {i}",
                    "advertiser": "Mock Advertiser",
                    "category": "finance" if i % 2 == 0 else "software",
                    "geo": "US" if i % 2 == 0 else "CA",
                    "payout": 12.0 + (i % 9) * 2.5,
                    "payout_type": "CPA",
                    "epc": 5.0 + (i % 10) * 1.5,
                    "conversion_rate": round(0.02 + (i % 7) * 0.005, 4),
                    "allowed_traffic_types": traffic_types,
                    "email_allowed": email_allowed,
                    "email_approval_required": False,
                    "status": "active",
                }
            )
        return offers

    async def build_tracking_link(self, offer_id: str, sub_id: str) -> str:
        return f"https://affiliate.mock/tracking?offer_id={offer_id}&sub_id={sub_id}"

    async def sync_conversions(self, since_timestamp):
        return []

    async def sync_reports(self, since_timestamp):
        return []
