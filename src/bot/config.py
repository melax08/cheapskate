from pathlib import Path

from pydantic import SecretStr, computed_field, field_validator
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Telegram bot environment variables."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        extra="allow",
    )

    bot_telegram_token: SecretStr
    echo_messages: bool = True
    allowed_telegram_ids: str | None = None

    redis_host: str
    redis_port: int
    redis_db: int

    @computed_field
    @property
    def redis_url(self) -> str:
        return str(
            MultiHostUrl.build(
                scheme="redis",
                host=self.redis_host,
                port=self.redis_port,
                path=str(self.redis_db),
            )
        )

    @field_validator("allowed_telegram_ids")
    @classmethod
    def convert_string_to_set(cls, data: str) -> set[int] | None:
        """Convert dot variable string like: 123 321 to set of integers."""
        if data is not None:
            data = set(map(int, data.split()))
        return data


bot_settings = Settings()
