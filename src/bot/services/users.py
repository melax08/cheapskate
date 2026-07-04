from aiogram.types import User

from bot.api_requests import APIClient


async def register_user(user: User, client: APIClient):
    await client.register_user(
        telegram_id=user.id,
        telegram_username=user.username,
        telegram_first_name=user.first_name,
        telegram_last_name=user.last_name,
    )
