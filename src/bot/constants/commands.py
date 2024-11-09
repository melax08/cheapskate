from aiogram.types.bot_command import BotCommand

ADD_CURRENCY_COMMAND = "add_currency"
STATISTICS_COMMAND = "statistics"
MONEY_LEFT_COMMAND = "money_left"
TODAY_COMMAND = "today"
ADD_CATEGORY_COMMAND = "add_category"
CANCEL_COMMAND = "cancel"

COMMANDS = [
    BotCommand(command=MONEY_LEFT_COMMAND, description="Остаток средств на месяц"),
    BotCommand(command=TODAY_COMMAND, description="Сегодняшние траты"),
    BotCommand(
        command=STATISTICS_COMMAND, description="Посмотреть статистику за период"
    ),
    BotCommand(command=ADD_CATEGORY_COMMAND, description="Добавить категорию трат"),
    BotCommand(command=ADD_CURRENCY_COMMAND, description="Добавить валюту"),
    BotCommand(command="settings", description="Настройки приложения"),
    BotCommand(command=CANCEL_COMMAND, description="Отменить действие"),
]
