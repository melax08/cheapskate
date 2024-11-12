from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.api_requests import APIClient
from bot.constants import telegram_messages
from bot.constants.commands import TODAY_COMMAND
from bot.utils import append_currencies_categories_expenses_info

router = Router()


@router.message(Command(TODAY_COMMAND))
async def today_expenses(message: Message, client: APIClient) -> None:
    """Sends the user message with information about today expenses."""
    response_data = await client.get_today_expenses()

    currencies = response_data["currencies"]

    if not currencies:
        await message.answer(telegram_messages.NO_TODAY_EXPENSES)
    else:
        message_to_user = [telegram_messages.TODAY_EXPENSES]
        append_currencies_categories_expenses_info(currencies, message_to_user)

        await message.answer("\n".join(message_to_user))
