import datetime as dt
from dataclasses import asdict, dataclass
from typing import Self

from bot.constants.telegram_messages import REPORT_INFO
from bot.serializers.base import BaseSerializer


@dataclass
class Report(BaseSerializer):
    url: str
    updated_at: str

    def get_message(self) -> str:
        return REPORT_INFO.format(*asdict(self).values())

    @classmethod
    def from_api_response(cls, response_data: dict) -> Self:
        updated_at = response_data["updated_at"]
        updated_at = (
            dt.datetime.fromisoformat(response_data["updated_at"]).strftime("%d.%m.%y %H:%M")
            if updated_at
            else "-"
        )
        return cls(response_data["url"], updated_at)
