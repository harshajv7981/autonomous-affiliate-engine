from abc import ABC, abstractmethod


class AffiliateNetworkAdapter(ABC):
    @abstractmethod
    async def sync_offers(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    async def build_tracking_link(self, offer_id: str, sub_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def sync_conversions(self, since_timestamp):
        raise NotImplementedError

    @abstractmethod
    async def sync_reports(self, since_timestamp):
        raise NotImplementedError
