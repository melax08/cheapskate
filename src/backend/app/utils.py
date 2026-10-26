import asyncio
from contextlib import suppress

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import AiogramError
from fastapi import HTTPException, status

from backend.app.core.config import settings
from backend.app.models import User
from configs.enums import APIErrorCode


def raise_api_error(error_code: APIErrorCode, message: str, status_code: status) -> None:
    """Raise http error with the specified body structure."""
    raise HTTPException(
        status_code=status_code,
        detail={"error_code": error_code, "message": message},
    )


async def send_message_to_authorized_users_about_user_action(user: User, message: str) -> None:
    if not settings.echo_messages or not settings.allowed_telegram_ids:
        return

    authorized_ids_without_author = settings.allowed_telegram_ids.copy()
    authorized_ids_without_author.discard(user.telegram_id)
    if not authorized_ids_without_author:
        return

    message_header = f"Действие от {user.telegram_first_name}" + (
        f" {user.telegram_last_name}" if user.telegram_last_name else ""
    )
    final_message = f"{message_header}: {message}"

    async with Bot(token=settings.bot_telegram_token.get_secret_value()) as bot:
        await asyncio.gather(
            *[
                send_telegram_message(bot, telegram_id, final_message)
                for telegram_id in authorized_ids_without_author
            ]
        )


async def send_telegram_message(bot: Bot, telegram_id: int, message: str) -> None:
    with suppress(AiogramError):
        await bot.send_message(telegram_id, message, parse_mode=ParseMode.HTML)
