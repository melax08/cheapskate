import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (CallbackQueryHandler, ContextTypes, MessageHandler,
                          filters)

from bot.api_requests import client
from bot.constants.logging_messages import (CHOOSE_CATEGORY_LOG,
                                            DELETE_EXPENSE_FROM_API_LOG,
                                            NO_CATEGORIES_LOG,
                                            SPEND_EXPENSE_TO_API_LOG,
                                            WRONG_EXPENSE_LOG)
from bot.constants.telegram_messages import (CHOOSE_CATEGORY, DELETE_MESSAGE,
                                             NO_CATEGORIES, UPDATE_MESSAGE,
                                             WRONG_REQUEST)
from bot.utils import auth, create_category_keyboard, get_user_info
from bot.validators import money_validator


@auth
async def add_expense(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """The user has to write the amount of money he spent."""
    try:
        money = money_validator(update.message.text)
    except ValueError:
        logging.info(WRONG_EXPENSE_LOG.format(
            get_user_info(update),
            update.message.text)
        )
        await update.message.reply_text(WRONG_REQUEST)
        return

    try:
        keyboard = await create_category_keyboard(money)
    except ValueError:
        logging.warning(NO_CATEGORIES_LOG.format(get_user_info(update)))
        await update.message.reply_text(NO_CATEGORIES)
        return

    logging.info(CHOOSE_CATEGORY_LOG.format(get_user_info(update), money))
    await update.message.reply_text(
        CHOOSE_CATEGORY.format(money),
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


@auth
async def select_expense_category(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """The user must select the expense category by clicking
    on one of the buttons."""
    query = update.callback_query
    money, category_id = query.data.split()
    response_data = await client.send_expense(money, category_id)
    logging.info(SPEND_EXPENSE_TO_API_LOG.format(
        get_user_info(update),
        money,
        response_data['category']['name'],
        response_data['money_left'])
    )
    await query.answer()
    await query.edit_message_text(
        text=UPDATE_MESSAGE.format(
            money,
            response_data['category']['name'],
            response_data['money_left']
        ),
        reply_markup=InlineKeyboardMarkup.from_row(
            [InlineKeyboardButton(
                'Удалить',
                callback_data=f'DEL {response_data["id"]}'
            )]
        ),
        parse_mode=ParseMode.HTML
    )


@auth
async def delete_expense(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """When the user clicks the 'delete' button under message,
    the expense deleted by its id."""
    query = update.callback_query
    expense_to_delete_id = ''.join(query.data.split()[1:])
    response_data = await client.delete_expense(expense_to_delete_id)
    logging.info(DELETE_EXPENSE_FROM_API_LOG.format(
        get_user_info(update),
        response_data['amount'],
        response_data['category']['name'],
        response_data['money_left'])
    )
    await query.answer()
    await query.edit_message_text(
        text=DELETE_MESSAGE.format(
            response_data['amount'],
            response_data['category']['name'],
            response_data['money_left']
        ),
        parse_mode=ParseMode.HTML
    )


add_expense_handler = MessageHandler(filters.TEXT, add_expense)
select_category_handler = CallbackQueryHandler(select_expense_category)
delete_expense_handler = CallbackQueryHandler(
    delete_expense, pattern=r'DEL \d+'
)
