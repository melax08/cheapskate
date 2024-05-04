from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_title: str = "Cheapskate"
    app_description: str = "<Application for financial control>"
    database_url: str = "sqlite+aiosqlite:///./fastapi.db"
    secret: str = "SECRET"

    model_config = SettingsConfigDict(
        env_prefix="api_",
        env_file=Path(__file__).parent.parent.parent.parent / ".env",
        extra="allow",
    )


settings = Settings()
