from typing import Any, Awaitable, Callable, Dict

import aiohttp
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from configs.api_settings import API_URL
from yarl import URL

from bot.api_requests import APIClient
from bot.constants.constants import REQUEST_API_TIMEOUT


class HTTPClientMiddleware(BaseMiddleware):
    """Add HTTP client to the handler."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with aiohttp.ClientSession(conn_timeout=REQUEST_API_TIMEOUT) as session:
            data["client"] = APIClient(api_url=URL(API_URL), session=session)
            return await handler(event, data)
