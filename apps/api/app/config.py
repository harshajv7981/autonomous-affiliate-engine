from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "autonomous-affiliate-engine"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5433/affiliate_engine"
    redis_url: str = "redis://localhost:6379/0"
    system_active: bool = True  # kill switch; never LLM-gated
    # Sender identity + unsubscribe are required on every send (compliance gate blocks without them).
    sender_name: str = "Affiliate Engine Lab"
    sender_email: str = "lab@example.test"
    sender_postal_address: str = "Simulation only - set a real postal address before sending"
    unsubscribe_base_url: str = "http://localhost:8008/unsubscribe"
    frequency_cap_per_run: int = 1  # max campaigns per audience per engine run

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
