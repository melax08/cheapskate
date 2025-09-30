from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Self

from bot.constants.telegram_messages import SETTINGS_INFO
from bot.serializers.base import BaseSerializer


@dataclass
class Settings(BaseSerializer):
    """Settings serializer."""

    currency_name: str
    currency_code: str
    budget: Decimal

    def get_message(self) -> str:
        return SETTINGS_INFO.format(*asdict(self).values())

    @classmethod
    def from_api_response(cls, response_data: dict) -> Self:
        """Create settings instance from API response json."""
        return cls(
            response_data["default_currency"]["name"],
            response_data["default_currency"]["letter_code"],
            Decimal(response_data["budget"]).normalize(),
        )
