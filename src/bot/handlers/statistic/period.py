import calendar

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.api_requests import APIClient
from bot.callbacks.statistic import MonthCallback, YearCallback
from bot.constants import telegram_messages
from bot.constants.commands import STATISTICS_COMMAND
from bot.keyboards.statistic import (
    create_statistic_months_keyboard,
    create_statistic_years_keyboard,
)
from bot.utils.utils import (
    append_currencies_categories_expenses_info,
    get_russian_month_name,
)

router = Router()


@router.message(Command(STATISTICS_COMMAND))
async def get_years_with_expenses(message: Message, client: APIClient) -> None:
    """Send the user a keyboard with years with expenses."""
    keyboard = await create_statistic_years_keyboard(client)

    if keyboard:
        await message.answer(
            telegram_messages.STATISTIC_YEAR_MESSAGE, reply_markup=keyboard
        )
    else:
        await message.answer(telegram_messages.NO_EXPENSES)


@router.callback_query(YearCallback.filter())
async def get_months_in_year_with_expenses(
    callback: CallbackQuery, callback_data: YearCallback
) -> None:
    """Send the user a keyboard with a list of months for the specified year
    in which there were expenses."""
    keyboard = create_statistic_months_keyboard(
        callback_data.year, callback_data.months
    )
    await callback.message.edit_text(
        text=telegram_messages.STATISTIC_MONTH_MESSAGE, reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(MonthCallback.filter())
async def get_report_for_period(
    callback: CallbackQuery, callback_data: MonthCallback, client: APIClient
) -> None:
    """Get the expense statistic about chosen month and year."""
    statistic_data = await client.get_statistic(callback_data.year, callback_data.month)

    message = [
        telegram_messages.PERIOD_EXPENSES.format(
            get_russian_month_name(calendar.month_name[callback_data.month]),
            callback_data.year,
        )
    ]

    append_currencies_categories_expenses_info(statistic_data["currencies"], message)

    await callback.message.edit_text(text="\n".join(message))
    await callback.answer()
