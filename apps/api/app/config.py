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
    # Base URL that recipients' mail clients can reach (click, unsubscribe, mock network links).
    public_base_url: str = "http://localhost:8008"
    frequency_cap_per_run: int = 1  # max campaigns per audience per engine run
    # Real sends go ONLY to these comma-separated addresses (inboxes you own). Empty = no real sends.
    test_recipients: str = ""
    track_opens: bool = True  # 1x1 pixel; opens are approximate (Apple Mail prefetches, some clients block)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""  # Gmail: an app password, never your account password
    clickbank_api_key: str = ""  # ClickBank > Settings > API keys; needs api_order_read
    # AI copy for real sends: "ollama" (local, free) or "none" (deterministic templates).
    llm_provider: str = "none"
    ollama_url: str = "http://localhost:11434"
    llm_model: str = "qwen3.5:9b"
    llm_timeout_seconds: float = 120.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
