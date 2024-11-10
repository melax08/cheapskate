from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from bot.api_requests import APIClient
from bot.constants.commands import SETTINGS_COMMAND
from bot.keyboards.settings import settings_markup

router = Router()


@router.message(StateFilter(None), Command(SETTINGS_COMMAND))
async def get_settings_cmd(message: Message, client: APIClient) -> None:
    """Get information about current application settings."""
    settings = await client.get_settings()

    await message.answer(
        settings.get_settings_message(),
        reply_markup=settings_markup,
    )
