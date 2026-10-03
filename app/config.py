import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./webhooks.db"
    WEBHOOK_SECRET: str = "your-local-secret"

    # Prioritize .env.local if present, fallback to .env
    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env") if os.path.exists(".env.local") else ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
