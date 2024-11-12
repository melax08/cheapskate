import logging

from aiogram import Bot, Router
from aiogram.types import CallbackQuery

from bot.api_requests import APIClient
from bot.callbacks.currencies import ExpenseCurrencyCallback
from bot.callbacks.expenses import ExpenseChangeCurrencyCallback
from bot.constants import logging_messages, telegram_messages
from bot.keyboards.currencies import create_currency_keyboard
from bot.keyboards.expenses import create_expense_manage_keyboard
from bot.utils import (
    get_user_info,
    normalize_amount,
    reply_message_to_authorized_users,
)

router = Router()


@router.callback_query(ExpenseChangeCurrencyCallback.filter())
async def change_currency(
    callback: CallbackQuery,
    callback_data: ExpenseChangeCurrencyCallback,
    client: APIClient,
) -> None:
    """User click 'change currency' button under expense
    message and get buttons with available currencies to set."""
    try:
        currency_keyboard = await create_currency_keyboard(
            callback_data.expense_id, client
        )
    except ValueError:
        logging.warning(
            logging_messages.NO_CURRENCIES_LOG.format(get_user_info(callback.from_user))
        )
        await callback.message.answer(telegram_messages.NO_CURRENCIES)
        return

    await callback.message.edit_text(
        text=telegram_messages.CHOOSE_CURRENCY.format(callback_data.amount),
        reply_markup=currency_keyboard,
    )
    await callback.answer()


@router.callback_query(ExpenseCurrencyCallback.filter())
async def currency_chosen(
    callback: CallbackQuery,
    callback_data: ExpenseCurrencyCallback,
    client: APIClient,
    bot: Bot,
) -> None:
    """Set the specified currency for specified expense."""
    response_data = await client.set_currency(
        callback_data.expense_id, callback_data.currency_id
    )

    message = telegram_messages.CURRENCY_SET.format(
        response_data["currency"]["name"],
        response_data["currency"]["letter_code"],
        normalize_amount(response_data["amount"]),
        response_data["category"]["name"],
    )
    logging.info(
        logging_messages.SET_CURRENCY_LOG.format(
            get_user_info(callback.from_user),
            response_data["currency"]["name"],
            response_data["id"],
        )
    )
    await callback.message.edit_text(
        message,
        reply_markup=create_expense_manage_keyboard(
            response_data.get("id"), response_data.get("amount")
        ),
    )
    await callback.answer()
    await reply_message_to_authorized_users(message, callback.from_user, bot)
