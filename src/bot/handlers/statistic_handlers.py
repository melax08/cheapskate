import calendar

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from bot.api_requests import get_api_client
from bot.constants.telegram_messages import (IN_CATEGORIES_LABEL, NO_EXPENSES,
                                             PERIOD_EXPENSES,
                                             SELECT_EXPENSE_PERIOD)
from bot.utils.keyboards import create_expense_periods_keyboard
from bot.utils.utils import (append_categories_expenses_info, auth,
                             get_russian_month_name)


@auth
async def get_periods_with_expenses(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Send to user the keyboard with all expense periods in database.
    The user can click on one of buttons and get a report about this period."""
    keyboard = await create_expense_periods_keyboard()
    if keyboard is not None:
        await update.message.reply_text(
            SELECT_EXPENSE_PERIOD,
            reply_markup=keyboard
        )
    else:
        await update.message.reply_text(NO_EXPENSES)


@auth
async def get_report_for_period(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Get the expense statistic about chosen month and year."""
    query = update.callback_query
    _, year, month = query.data.split()

    async with get_api_client() as client:
        statistic_data = await client.get_statistic(year, month)

    message = [
        PERIOD_EXPENSES.format(
            get_russian_month_name(calendar.month_name[int(month)]),
            year,
            statistic_data['money_spent']
        )
    ]

    append_categories_expenses_info(
        statistic_data['categories'],
        message,
        IN_CATEGORIES_LABEL
    )

    await query.edit_message_text(
        text='\n'.join(message),
        parse_mode=ParseMode.HTML
    )

expense_periods_handler = CommandHandler(
    'statistics', get_periods_with_expenses)
statistic_handler = CallbackQueryHandler(
    get_report_for_period, pattern=r'REP \d+')
