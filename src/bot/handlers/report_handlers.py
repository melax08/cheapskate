from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from bot.utils import auth, create_expense_periods_keyboard
from bot.constants.telegram_messages import SELECT_EXPENSE_PERIOD


@auth
async def get_periods_with_expenses(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Send to user the keyboard with all expense periods in database.
    The user can click on one of buttons and get a report about this period."""
    keyboard = await create_expense_periods_keyboard()
    await update.message.reply_text(
        SELECT_EXPENSE_PERIOD,
        reply_markup=InlineKeyboardMarkup([keyboard])
    )


@auth
async def get_report_for_period(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    _, year, month = query.data.split()

    await query.edit_message_text(
        text=f'Отчет за период: {year} {month}'
    )

expense_periods_handler = CommandHandler(
    'statistics', get_periods_with_expenses)
get_report_handler = CallbackQueryHandler(
    get_report_for_period, pattern=r'REP \d+')
