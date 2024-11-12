import logging

from aiogram import Bot, Router
from aiogram.types import CallbackQuery

from bot.api_requests import APIClient
from bot.callbacks.settings import (
    ChangeDefaultCurrencyCallback,
    SelectDefaultCurrencyCallback,
)
from bot.constants import logging_messages, telegram_messages
from bot.exceptions import APIError
from bot.keyboards.settings import create_default_currency_keyboard, settings_markup
from bot.utils import (
    get_user_info,
    reply_message_to_authorized_users,
)

router = Router()


@router.callback_query(ChangeDefaultCurrencyCallback.filter())
async def change_default_currency(
    callback: CallbackQuery,
    client: APIClient,
) -> None:
    """Show the list of available currencies to set as default currency."""
    try:
        currency_keyboard = await create_default_currency_keyboard(client)
        await callback.message.edit_text(
            text=telegram_messages.SELECT_NEW_DEFAULT_CURRENCY,
            reply_markup=currency_keyboard,
        )
    except ValueError:
        logging.warning(
            logging_messages.NO_CURRENCIES_LOG.format(get_user_info(callback.from_user))
        )
        await callback.message.answer(text=telegram_messages.NO_CURRENCIES)

    await callback.answer()


@router.callback_query(SelectDefaultCurrencyCallback.filter())
async def default_currency_chosen(
    callback: CallbackQuery,
    callback_data: SelectDefaultCurrencyCallback,
    client: APIClient,
    bot: Bot,
) -> None:
    """Set the new default currency for future expenses in the application."""
    try:
        settings = await client.set_default_currency(callback_data.currency_id)
    except APIError:
        logging.warning(
            logging_messages.WRONG_CURRENCY_LOG.format(
                get_user_info(callback.from_user), callback_data.currency_id
            )
        )
        currency_keyboard = await create_default_currency_keyboard(client)
        await callback.message.edit_text(
            text=telegram_messages.NONEXISTENT_CURRENCY,
            reply_markup=currency_keyboard,
        )
        await callback.answer()
        return

    logging.info(
        logging_messages.SET_NEW_DEFAULT_CURRENCY_LOG.format(
            get_user_info(callback.from_user), settings.currency_name
        )
    )
    await callback.message.edit_text(
        text=settings.get_settings_message_with_info(
            telegram_messages.NEW_DEFAULT_CURRENCY_SET_SUCCESS
        ),
        reply_markup=settings_markup,
    )
    await callback.answer()

    await reply_message_to_authorized_users(
        (
            f"{telegram_messages.NEW_DEFAULT_CURRENCY_SET_SUCCESS} "
            f"{settings.currency_name} ({settings.currency_code})"
        ),
        callback.from_user,
        bot,
    )
