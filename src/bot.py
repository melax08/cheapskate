from telegram.ext import Application

from bot.handlers import (
    spending_money_handler,
    choose_category_handler,
    delete_expense_handler
)
from bot.constants import TOKEN


def start_bot() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handlers(
        (
            spending_money_handler,
            delete_expense_handler,
            choose_category_handler
        )
    )
    application.run_polling()


if __name__ == '__main__':
    start_bot()
