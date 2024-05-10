from pathlib import Path
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Telegram bot environment variables."""

    token: str
    echo_messages: bool = True
    allowed_telegram_ids: Optional[str] = None

    model_config = SettingsConfigDict(
        env_prefix="bot_",
        env_file=Path(__file__).parent.parent / ".env",
        extra="allow",
    )

    @field_validator("allowed_telegram_ids")
    @classmethod
    def convert_string_to_set(cls, data: str) -> Optional[set[int]]:
        """Convert dot variable string like: 123 321 to set of integers."""
        if data is not None:
            data = set(map(int, data.split()))
        return data


bot_settings = Settings()
