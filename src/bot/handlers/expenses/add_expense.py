import logging
from decimal import InvalidOperation

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, Message

from bot.api_requests import APIClient
from bot.callbacks.expenses import ExpenseCategoryCallback
from bot.constants import logging_messages, telegram_messages
from bot.keyboards.expenses import (
    create_category_keyboard,
    create_expense_manage_keyboard,
)
from bot.services.expenses import parse_and_sum_expenses_from_message
from bot.utils.utils import (
    get_user_info,
    money_left_calculate_message,
    normalize_amount,
    reply_message_to_authorized_users,
)
from bot.utils.validators import expense_amount_validator

router = Router()


@router.message(F.text)
async def add_expense(message: Message, client: APIClient) -> None:
    """Parse expense amount and show the keyboard with categories to the user."""
    try:
        expense_amount = parse_and_sum_expenses_from_message(message.text)
        expense_amount_validator(expense_amount)
        expense_amount = normalize_amount(expense_amount)
    except (ValueError, InvalidOperation):
        logging.info(
            logging_messages.WRONG_EXPENSE_LOG.format(
                get_user_info(message.from_user), message.text
            )
        )
        await message.answer(telegram_messages.WRONG_REQUEST)
        return

    try:
        keyboard = await create_category_keyboard(expense_amount, client)
    except ValueError:
        logging.warning(
            logging_messages.NO_CATEGORIES_LOG.format(get_user_info(message.from_user))
        )
        await message.answer(telegram_messages.NO_CATEGORIES)
        return

    logging.info(
        logging_messages.CHOOSE_CATEGORY_LOG.format(
            get_user_info(message.from_user), expense_amount
        )
    )
    await message.answer(
        telegram_messages.CHOOSE_CATEGORY.format(expense_amount), reply_markup=keyboard
    )


@router.callback_query(ExpenseCategoryCallback.filter())
async def expense_category_chosen(
    callback: CallbackQuery,
    callback_data: ExpenseCategoryCallback,
    client: APIClient,
    bot: Bot,
) -> None:
    """Send the information about chosen expense category to the API."""
    response_data = await client.add_expense(
        callback_data.amount, callback_data.category_id
    )

    logging.info(
        logging_messages.SPEND_EXPENSE_TO_API_LOG.format(
            get_user_info(callback.from_user),
            callback_data.amount,
            response_data["category"]["name"],
            response_data["money_left"],
        )
    )

    money_left, message = money_left_calculate_message(
        response_data["money_left"], telegram_messages.UPDATE_MESSAGE
    )

    expense_amount = normalize_amount(callback_data.amount)
    message = message.format(
        expense_amount,
        response_data["currency"]["letter_code"],
        response_data["category"]["name"],
        money_left,
    )
    await callback.message.edit_text(
        text=message,
        reply_markup=create_expense_manage_keyboard(
            response_data["id"], expense_amount
        ),
    )
    await callback.answer()
    await reply_message_to_authorized_users(message, callback.from_user, bot)
