import calendar

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from bot.api_requests import get_api_client
from bot.constants.telegram_messages import (
    NO_EXPENSES,
    PERIOD_EXPENSES,
    STATISTIC_MONTH_MESSAGE,
    STATISTIC_YEAR_MESSAGE,
)
from bot.utils.keyboards import (
    create_statistic_months_keyboard,
    create_statistic_years_keyboard,
)
from bot.utils.utils import (
    append_currencies_categories_expenses_info,
    auth,
    get_russian_month_name,
)


@auth
async def get_years_with_expenses(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Send the user a keyboard with years with expenses."""
    keyboard = await create_statistic_years_keyboard()
    if keyboard:
        await update.message.reply_text(STATISTIC_YEAR_MESSAGE, reply_markup=keyboard)
    else:
        await update.message.reply_text(NO_EXPENSES)


@auth
async def get_months_in_year_with_expenses(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Send the user a keyboard with a list of months for the specified year
    in which there were expenses."""
    query = update.callback_query
    _, year, months = query.data.split()

    keyboard = create_statistic_months_keyboard(year, months)
    await query.edit_message_text(text=STATISTIC_MONTH_MESSAGE, reply_markup=keyboard)


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
        )
    ]

    append_currencies_categories_expenses_info(statistic_data["currencies"], message)

    await query.edit_message_text(text="\n".join(message), parse_mode=ParseMode.HTML)


statistic_initial_handler = CommandHandler("statistics", get_years_with_expenses)
statistic_year_handler = CallbackQueryHandler(
    get_months_in_year_with_expenses, pattern=r"YEAR \d+"
)
statistic_report_handler = CallbackQueryHandler(
    get_report_for_period, pattern=r"REP \d+"
)
