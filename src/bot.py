from telegram.ext import Application

from bot.handlers.add_category_conversation import add_category_handler
from bot.handlers.command_handlers import money_left_handler, today_handler
from bot.handlers.expense_handlers import (add_expense_handler,
                                           delete_expense_handler,
                                           select_category_handler)
from bot.handlers.main_handlers import error_handler, start_handler
from utils.configs import TOKEN
from utils.logger import configure_logging


def start_bot() -> None:
    """Configure telegram bot application, add telegram handlers and run
    polling."""
    application = Application.builder().token(TOKEN).build()
    application.add_error_handler(error_handler)
    application.add_handlers(
        (
            start_handler,
            add_category_handler,
            money_left_handler,
            today_handler,
            add_expense_handler,
            delete_expense_handler,
            select_category_handler,
        )
    )
    application.run_polling()


if __name__ == '__main__':
    configure_logging()
    start_bot()
