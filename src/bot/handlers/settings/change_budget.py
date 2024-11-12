import logging

from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.api_requests import APIClient
from bot.callbacks.settings import ChangeBudgetCallback
from bot.constants import logging_messages, telegram_messages
from bot.keyboards.settings import settings_markup
from bot.states.settings import ChangeBudgetState
from bot.utils import get_user_info, reply_message_to_authorized_users
from bot.validators import budget_validator

router = Router()


@router.callback_query(ChangeBudgetCallback.filter())
async def change_budget(callback: CallbackQuery, state: FSMContext) -> None:
    """Change the month budget of expenses in application."""
    await callback.message.edit_text(text=telegram_messages.ENTER_NEW_BUDGET)
    await state.set_state(ChangeBudgetState.writing_month_budget)
    await callback.answer()


@router.message(ChangeBudgetState.writing_month_budget)
async def change_budget_written(
    message: Message, state: FSMContext, client: APIClient, bot: Bot
) -> None:
    """Confirm changing of month budget of expenses in application."""
    new_budget = message.text.strip()

    try:
        new_budget = budget_validator(new_budget)
        settings = await client.set_budget(new_budget)

        logging.info(
            logging_messages.SET_NEW_BUDGET_LOG.format(
                get_user_info(message.from_user), new_budget
            )
        )

        await message.answer(
            text=settings.get_settings_message_with_info(
                telegram_messages.NEW_BUDGET_SET_SUCCESS
            ),
            reply_markup=settings_markup,
        )
        await state.clear()
        await reply_message_to_authorized_users(
            source_message=(
                f"{telegram_messages.NEW_BUDGET_SET_SUCCESS} {settings.budget}"
            ),
            user=message.from_user,
            bot=bot,
        )
    except ValueError:
        logging.warning(
            logging_messages.WRONG_BUDGET_LOG.format(
                get_user_info(message.from_user), new_budget
            )
        )
        await message.answer(telegram_messages.WRONG_NEW_BUDGET)
