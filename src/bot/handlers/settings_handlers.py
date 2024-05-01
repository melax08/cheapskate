import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from bot.api_requests import get_api_client
from bot.constants.logging_messages import (
    NO_CURRENCIES_LOG,
    SET_NEW_DEFAULT_CURRENCY_LOG,
    WRONG_CURRENCY_LOG,
)
from bot.constants.telegram_messages import (
    NEW_DEFAULT_CURRENCY_SET_SUCCESS,
    NO_CURRENCIES,
    NONEXISTENT_CURRENCY,
    SELECT_NEW_DEFAULT_CURRENCY,
    SETTINGS_INFO,
)
from bot.exceptions import APIError
from bot.utils.keyboards import select_default_currency_keyboard, settings_markup
from bot.utils.utils import auth, get_user_info, reply_message_to_authorized_users


@auth
async def get_settings_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Command to get information about current application settings."""
    async with get_api_client() as client:
        response_data = await client.get_settings()
        currency_data = response_data.get("default_currency")

    await update.message.reply_html(
        SETTINGS_INFO.format(
            currency_data.get("name"),
            currency_data.get("letter_code"),
            response_data.get("budget"),
        ),
        reply_markup=settings_markup,
    )


@auth
async def change_default_currency(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Show the list of available currencies to set as default currency."""
    query = update.callback_query

    try:
        currency_keyboard = await select_default_currency_keyboard()
    except ValueError:
        logging.warning(NO_CURRENCIES_LOG.format(get_user_info(update)))
        await query.edit_message_text(text=NO_CURRENCIES, reply_markup=None)
        return

    await query.edit_message_text(
        text=SELECT_NEW_DEFAULT_CURRENCY,
        reply_markup=currency_keyboard,
    )


@auth
async def set_default_currency(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Set the new default currency for future expenses in the application."""
    query = update.callback_query
    _, currency_id = query.data.split()

    async with get_api_client() as client:
        try:
            response_data = await client.set_default_currency(int(currency_id))
            currency_data = response_data.get("default_currency")
        except APIError:
            logging.warning(
                WRONG_CURRENCY_LOG.format(get_user_info(update), currency_id)
            )
            currency_keyboard = await select_default_currency_keyboard()
            await query.edit_message_text(
                text=NONEXISTENT_CURRENCY,
                reply_markup=currency_keyboard,
            )
            return

    await query.answer()
    logging.info(
        SET_NEW_DEFAULT_CURRENCY_LOG.format(
            get_user_info(update), currency_data.get("name")
        )
    )
    await query.edit_message_text(
        text=NEW_DEFAULT_CURRENCY_SET_SUCCESS
        + "\n\n"
        + SETTINGS_INFO.format(
            currency_data.get("name"),
            currency_data.get("letter_code"),
            response_data.get("budget"),
        ),
        reply_markup=settings_markup,
        parse_mode=ParseMode.HTML,
    )
    await reply_message_to_authorized_users(
        NEW_DEFAULT_CURRENCY_SET_SUCCESS
        + f" {currency_data.get('name')} ({currency_data.get('letter_code')})",
        update,
    )


settings_handler = CommandHandler("settings", get_settings_handler)
change_default_currency_handler = CallbackQueryHandler(
    change_default_currency, pattern="change_currency"
)
set_default_currency_handler = CallbackQueryHandler(
    set_default_currency, pattern=r"DEFAULT_CUR \d+"
)
