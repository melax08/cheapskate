import datetime as dt

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.api_requests import APIClient
from bot.constants import telegram_messages
from bot.constants.commands import MONEY_LEFT_COMMAND
from bot.utils.utils import (
    append_currencies_categories_expenses_info,
    get_russian_month_name,
    money_left_calculate_message,
    normalize_amount,
)

router = Router()


@router.message(Command(MONEY_LEFT_COMMAND))
async def money_left(message: Message, client: APIClient) -> None:
    """Sends the user a message with information about the remaining funds for
    the current month and information about spending by categories in currencies."""
    response_data = await client.get_money_left()

    current_datetime = dt.datetime.fromisoformat(response_data["current_datetime"])

    current_month = get_russian_month_name(current_datetime.strftime("%B"))

    money_left, message_to_user = money_left_calculate_message(
        response_data["money_left"], telegram_messages.MONEY_LEFT_MESSAGE
    )

    message_to_user = [
        message_to_user.format(
            current_month,
            normalize_amount(response_data["budget"]),
            normalize_amount(response_data["money_spent"]),
            money_left,
            currency_code=response_data["default_currency"]["letter_code"],
        )
    ]

    append_currencies_categories_expenses_info(
        response_data["currencies"],
        message_to_user,
        telegram_messages.MONTH_CATEGORIES_LABEL,
    )

    await message.answer("\n".join(message_to_user))
