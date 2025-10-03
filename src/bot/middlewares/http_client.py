import logging
from collections.abc import Awaitable, Callable
from typing import Any

import aiohttp
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from yarl import URL

from bot.api_requests import APIClient
from bot.constants import logging_messages, telegram_messages
from bot.constants.constants import REQUEST_API_TIMEOUT
from bot.exceptions import APIError
from bot.utils import get_user_info
from configs.api_settings import API_URL


class HTTPClientMiddleware(BaseMiddleware):
    """Add HTTP client to the handler."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with aiohttp.ClientSession(conn_timeout=REQUEST_API_TIMEOUT) as session:
            try:
                data["client"] = APIClient(api_url=URL(API_URL), session=session)
                return await handler(event, data)
            except APIError as error:
                logging.info(
                    logging_messages.API_ERROR.format(
                        user=get_user_info(event.from_user),
                        url=error.info["url"],
                        error_code=error.error_code,
                    )
                )
                await event.answer(
                    telegram_messages.API_COMMON_ERROR.format(error_message=error.message)
                )
