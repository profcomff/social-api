import os
from functools import lru_cache

from pydantic import ConfigDict, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    model_config = ConfigDict(case_sensitive=True, env_file=".env", extra="allow")

    DB_DSN: PostgresDsn = 'postgresql://postgres@localhost:5432/postgres'
    ROOT_PATH: str = '/' + os.getenv('APP_NAME', '')

    CORS_ALLOW_ORIGINS: list[str] = ['*']
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ['*']
    CORS_ALLOW_HEADERS: list[str] = ['*']

    TELEGRAM_BOT_TOKEN: str | None = None

    GITHUB_APP_ID: int | None = None
    GITHUB_WEBHOOK_SECRET: str | None = None
    GITHUB_PRIVATE_KEY: str | None = None

    DISCORD_PUBLIC_KEY: str | None = None


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    return settings
