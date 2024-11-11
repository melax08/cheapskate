import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types.menu_button_commands import MenuButtonCommands
from configs.logger import configure_logging

from bot.config import bot_settings
from bot.constants.commands import COMMANDS
from bot.handlers.categories import router as categories_router
from bot.handlers.common import router as common_router
from bot.handlers.currencies import router as currencies_router
from bot.handlers.errors import router as errors_router
from bot.handlers.expenses import router as expenses_router
from bot.handlers.settings import router as settings_router
from bot.handlers.statistic import router as statistic_router
from bot.middlewares.auth import AuthMiddleware
from bot.middlewares.http_client import HTTPClientMiddleware

# ToDo: test error handler on messages, callbacks
# ToDo: move utils and validators outside utils package
# ToDo: update README.md
# ToDo: change name of state to InstanceState (like in settings state)


async def on_startup(bot: Bot) -> None:
    """Setup some bot configurations on bot startup."""
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=COMMANDS)
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())


async def start_bot() -> None:
    """Configure telegram bot application, add telegram handlers and run
    polling."""
    storage = RedisStorage.from_url(
        f"redis://{bot_settings.redis_host}:{bot_settings.redis_port}/{bot_settings.redis_db}"
    )
    dp = Dispatcher(storage=storage)

    dp.message.middleware(HTTPClientMiddleware())
    dp.callback_query.middleware(HTTPClientMiddleware())
    dp.message.outer_middleware(
        AuthMiddleware(allowed_telegram_ids=bot_settings.allowed_telegram_ids)
    )
    dp.callback_query.outer_middleware(
        AuthMiddleware(allowed_telegram_ids=bot_settings.allowed_telegram_ids)
    )

    dp.include_routers(
        errors_router,
        common_router,
        statistic_router,
        categories_router,
        currencies_router,
        settings_router,
        expenses_router,
    )

    dp.startup.register(on_startup)

    bot = Bot(
        token=bot_settings.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await dp.start_polling(bot)

    # application = Application.builder().token(bot_settings.token).build()
    # application.add_error_handler(error_handler)
    # application.add_handlers(
    #     (
    #         start_handler,
    #         settings_handler,
    #         change_default_currency_handler,
    #         set_default_currency_handler,
    #         change_currency_handler,
    #         set_budget_handler,
    #         set_currency_handler,
    #         add_category_handler,
    #         add_currency_handler,
    #         money_left_handler,
    #         today_handler,
    #         statistic_initial_handler,
    #         statistic_year_handler,
    #         statistic_report_handler,
    #         add_expense_handler,
    #         delete_expense_handler,
    #         select_category_handler,
    #     )
    # )
    # application.run_polling()


if __name__ == "__main__":
    configure_logging()
    asyncio.run(start_bot())
