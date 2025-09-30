from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.callbacks.report import ReportUpdateCallback


def create_report_keyboard() -> InlineKeyboardMarkup:
    """Create settings keyboard markup."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Обновить отчет",
                    callback_data=ReportUpdateCallback().pack(),
                ),
            ]
        ]
    )


report_markup = create_report_keyboard()
