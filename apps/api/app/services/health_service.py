class HealthService:
    def get_health(self) -> dict[str, str]:
        return {"status": "ok"}

    def get_readiness(self) -> dict[str, str]:
        return {"status": "ready"}
