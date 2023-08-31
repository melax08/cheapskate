from telegram.ext import Application

from bot.handlers import (
    spending_money_handler,
    choose_category_handler,
    delete_expense_handler,
    money_left_handler,
    start_handler
)
from utils.configs import TOKEN
from utils.logger import configure_logging


def start_bot() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handlers(
        (
            start_handler,
            money_left_handler,
            spending_money_handler,
            delete_expense_handler,
            choose_category_handler,
        )
    )
    application.run_polling()


if __name__ == '__main__':
    configure_logging()
    start_bot()
