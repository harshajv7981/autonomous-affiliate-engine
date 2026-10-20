from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "autonomous-affiliate-engine"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5433/affiliate_engine"
    redis_url: str = "redis://localhost:6379/0"
    system_active: bool = True  # kill switch; never LLM-gated

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
