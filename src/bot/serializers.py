from dataclasses import asdict, dataclass
from decimal import Decimal

from bot.constants.telegram_messages import SETTINGS_INFO


@dataclass
class Settings:
    """Settings serializer."""

    currency_name: str
    currency_code: str
    budget: Decimal

    def get_settings_message(self) -> str:
        """Get telegram message with settings information."""
        return SETTINGS_INFO.format(*asdict(self).values())

    def get_settings_message_with_info(self, info_message: str) -> str:
        """Get telegram settings message with additional information."""
        return f"{info_message}\n\n{self.get_settings_message()}"

    @classmethod
    def from_api_response(cls, response_data: dict):
        """Create settings instance from API response json."""
        return cls(
            response_data["default_currency"]["name"],
            response_data["default_currency"]["letter_code"],
            Decimal(response_data["budget"]).normalize(),
        )
