import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonCommands
)
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    CommandHandler
)

from .messages import (
    WRONG_REQUEST,
    UPDATE_MESSAGE,
    CHOOSE_CATEGORY,
    DELETE_MESSAGE,
    MONEY_LEFT_MESSAGE,
    START_MESSAGE
)
from .logging_messages import (
    START_BOT_LOG,
    WRONG_EXPENSE_LOG,
    CHOOSE_CATEGORY_LOG,
    SPEND_EXPENSE_TO_API_LOG,
    DELETE_EXPENSE_FROM_API_LOG
)
from .validators import money_validator
from .commands import COMMANDS
from .api_requests import client
from .utils import create_category_keyboard, get_user_info


async def start(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    logging.info(START_BOT_LOG.format(get_user_info(update)))
    bot_commands = await context.bot.get_my_commands()
    if not bot_commands:
        await context.bot.set_my_commands(commands=COMMANDS)
        await context.bot.set_chat_menu_button(
            menu_button=MenuButtonCommands()
        )

    await update.message.reply_html(
        START_MESSAGE.format(update.effective_user.mention_html())
    )


async def spending_money(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    try:
        money = money_validator(update.message.text)
    except ValueError:
        logging.info(WRONG_EXPENSE_LOG.format(
            get_user_info(update),
            update.message.text)
        )
        await update.message.reply_text(WRONG_REQUEST)
        return

    keyboard = await create_category_keyboard(money)

    logging.info(CHOOSE_CATEGORY_LOG.format(get_user_info(update), money))
    await update.message.reply_text(
        CHOOSE_CATEGORY.format(money),
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


async def choose_category(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    money, category_id = query.data.split()
    response_data = await client.send_expense(money, category_id)
    logging.info(SPEND_EXPENSE_TO_API_LOG.format(
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


async def delete_expense(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    expense_to_delete_id = ''.join(query.data.split()[1:])
    response_data = await client.delete_expense(expense_to_delete_id)
    logging.info(DELETE_EXPENSE_FROM_API_LOG.format(
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


async def get_money_left(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    response_data = await client.get_money_left()
    await update.message.reply_text(MONEY_LEFT_MESSAGE.format(response_data))


spending_money_handler = MessageHandler(filters.TEXT, spending_money)
choose_category_handler = CallbackQueryHandler(choose_category)
delete_expense_handler = CallbackQueryHandler(
    delete_expense, pattern=r'DEL \d+'
)
money_left_handler = CommandHandler('money_left', get_money_left)
start_handler = CommandHandler('start', start)
