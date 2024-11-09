import logging

from aiogram import Bot, Router
from aiogram.types import CallbackQuery

from bot.api_requests import APIClient
from bot.callbacks.expenses import ExpenseDeleteCallback
from bot.constants import logging_messages, telegram_messages
from bot.utils.utils import (
    get_user_info,
    money_left_calculate_message,
    normalize_amount,
    reply_message_to_authorized_users,
)

router = Router()


@router.callback_query(ExpenseDeleteCallback.filter())
async def delete_expense(
    callback: CallbackQuery,
    callback_data: ExpenseDeleteCallback,
    client: APIClient,
    bot: Bot,
) -> None:
    """When the user clicks the 'delete' button under message,
    the expense deleted by its id on the API side."""
    response_data = await client.delete_expense(callback_data.expense_id)

    logging.info(
        logging_messages.DELETE_EXPENSE_FROM_API_LOG.format(
            get_user_info(callback.from_user),
            response_data["amount"],
            response_data["category"]["name"],
            response_data["money_left"],
        )
    )

    money_left, message = money_left_calculate_message(
        response_data["money_left"], telegram_messages.DELETE_MESSAGE
    )

    message = message.format(
        normalize_amount(response_data["amount"]),
        response_data["currency"]["letter_code"],
        response_data["category"]["name"],
        money_left,
    )

    await callback.message.edit_text(text=message)
    await callback.answer()
    await reply_message_to_authorized_users(message, callback.from_user, bot)
