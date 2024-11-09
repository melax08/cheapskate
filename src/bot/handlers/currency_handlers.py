import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.api_requests import get_api_client
from bot.constants.logging_messages import (
    NO_CURRENCIES_LOG,
    SET_CURRENCY_LOG,
)
from bot.constants.telegram_messages import (
    CHOOSE_CURRENCY,
    CURRENCY_SET,
    NO_CURRENCIES,
)
from bot.decorators import auth
from bot.utils.keyboards import create_currency_keyboard, create_delete_expense_keyboard
from bot.utils.utils import (
    get_user_info,
    normalize_amount,
    reply_message_to_authorized_users,
)

from .main_handlers import cancel

LETTER_CODE: int = 0
COUNTRY_NAME: int = 1
CONFIRMATION: int = 2


# @auth
# async def add_currency(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Start add currency conversation handler."""
#     await update.message.reply_html(
#         ENTER_CURRENCY_NAME,
#         reply_markup=ReplyKeyboardRemove(),
#     )
#     return LETTER_CODE


# @auth
# async def _letter_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Ask user to write the currency letter code."""
#     currency_name = update.message.text.strip()
#
#     try:
#         currency_name_validator(currency_name)
#     except ValueError:
#         logging.warning(
#             CURRENCY_NAME_TOO_LONG_LOG.format(get_user_info(update), currency_name)
#         )
#         await update.message.reply_html(
#             VALIDATION_ERROR_CURRENCY_NAME.format(MAX_CURRENCY_NAME_LENGTH)
#         )
#         return LETTER_CODE
#
#     context.user_data["currency_name"] = currency_name
#     await update.message.reply_html(ENTER_CURRENCY_CODE)
#     return COUNTRY_NAME


# @auth
# async def _country_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Ask user to write the currency country."""
#     currency_code = update.message.text.strip().upper()
#
#     try:
#         currency_code_validator(update.message.text)
#     except ValueError:
#         logging.warning(
#             CURRENCY_INCORRECT_CODE_LOG.format(get_user_info(update), currency_code)
#         )
#         await update.message.reply_html(VALIDATION_ERROR_CURRENCY_CODE)
#         return COUNTRY_NAME
#
#     context.user_data["currency_letter_code"] = currency_code
#     await update.message.reply_html(ENTER_CURRENCY_COUNTRY)
#
#     return CONFIRMATION


# @auth
# async def _confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Add currency to backend."""
#     country_name = update.message.text.strip()
#
#     try:
#         currency_country_validator(country_name)
#         async with get_api_client() as client:
#             response_data = await client.add_currency(
#                 context.user_data.get("currency_name"),
#                 context.user_data.get("currency_letter_code"),
#                 country_name,
#             )
#
#         message = CURRENCY_ADD_SUCCESS.format(
#             response_data.get("name"),
#             response_data.get("letter_code"),
#             response_data.get("country"),
#         )
#
#         logging.info(
#             CURRENCY_ADDED_NEW_LOG.format(
#                 get_user_info(update), response_data.get("name")
#             )
#         )
#         await update.message.reply_text(message, parse_mode=ParseMode.HTML)
#         await reply_message_to_authorized_users(message, update)
#         return ConversationHandler.END
#
#     except BadRequest:
#         logging.warning(CURRENCY_NOT_UNIQUE_LOG.format(get_user_info(update)))
#         await update.message.reply_html(CURRENCY_NOT_UNIQUE)
#         return ConversationHandler.END
#     except ValueError:
#         logging.warning(
#             CURRENCY_COUNTRY_TOO_LONG_LOG.format(get_user_info(update), country_name)
#         )
#         await update.message.reply_html(VALIDATION_ERROR_COUNTRY.format(COUNTRY_LENGTH))
#         return CONFIRMATION


@auth
async def change_currency(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Change the expense's currency."""
    query = update.callback_query
    await query.answer()

    _, expense_id, expense_amount = query.data.split()
    expense_amount = normalize_amount(expense_amount)

    try:
        currency_keyboard = await create_currency_keyboard(expense_id)
    except ValueError:
        logging.warning(NO_CURRENCIES_LOG.format(get_user_info(update)))
        await query.message.reply_html(NO_CURRENCIES)
        return

    await query.edit_message_text(
        text=CHOOSE_CURRENCY.format(expense_amount),
        reply_markup=currency_keyboard,
        parse_mode=ParseMode.HTML,
    )


@auth
async def set_currency(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set the specified currency for specified expense."""
    query = update.callback_query
    _, expense_id, currency_id = query.data.split()

    async with get_api_client() as client:
        response_data = await client.set_currency(expense_id, currency_id)

    message = CURRENCY_SET.format(
        response_data["currency"]["name"],
        response_data["currency"]["letter_code"],
        normalize_amount(response_data["amount"]),
        response_data["category"]["name"],
    )
    logging.info(
        SET_CURRENCY_LOG.format(
            get_user_info(update),
            response_data["currency"]["name"],
            response_data["id"],
        )
    )
    await query.answer()
    await query.edit_message_text(
        message,
        reply_markup=create_delete_expense_keyboard(
            response_data.get("id"), response_data.get("amount")
        ),
        parse_mode=ParseMode.HTML,
    )
    await reply_message_to_authorized_users(message, update)


add_currency_handler = ConversationHandler(
    entry_points=[CommandHandler("add_currency", add_currency)],
    states={
        LETTER_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, _letter_code)],
        COUNTRY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, _country_name)],
        CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, _confirmation)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

change_currency_handler = CallbackQueryHandler(change_currency, pattern=r"CUR \d+")

set_currency_handler = CallbackQueryHandler(set_currency, pattern=r"CURC \d+ \d+")
