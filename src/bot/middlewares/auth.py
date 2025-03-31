import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from bot.constants import logging_messages, telegram_messages
from bot.utils import get_user_info


class AuthMiddleware(BaseMiddleware):
    """
    Allows access only to those telegram ids that are listed in the
    allowed_telegram_ids. If allowed_telegram_ids is empty,
    then allows access to requests from all telegram users.
    """

    def __init__(self, allowed_telegram_ids: set[int] | list[int] | tuple[int, ...]) -> None:
        self.allowed_telegram_ids = allowed_telegram_ids

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User = data["event_from_user"]

        if self.allowed_telegram_ids and user.id not in self.allowed_telegram_ids:
            logging.warning(logging_messages.ACCESS_DENIED_LOG.format(get_user_info(user)))
            await event.answer(telegram_messages.ACCESS_DENIED)
            return

        return await handler(event, data)
