from telegram.ext import Application

from bot.handlers.main_handlers import start_handler
from bot.handlers.command_handlers import money_left_handler
from bot.handlers.expense_handlers import (
    add_expense_handler,
    select_category_handler,
    delete_expense_handler
)
from bot.handlers.add_category_conversation import add_category_handler

from utils.configs import TOKEN
from utils.logger import configure_logging


def start_bot() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handlers(
        (
            start_handler,
            add_category_handler,
            money_left_handler,
            add_expense_handler,
            delete_expense_handler,
            select_category_handler,
        )
    )
    application.run_polling()


if __name__ == '__main__':
    configure_logging()
    start_bot()
