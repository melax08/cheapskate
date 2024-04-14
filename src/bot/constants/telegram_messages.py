from bot.constants.commands import ADD_CURRENCY_COMMAND

ACCESS_DENIED = "Доступ запрещен 👀"

API_ERROR = (
    "‼️ Возникла внутренняя проблема при обработке запроса. "
    "Попробуйте повторить данное действие позже."
)

WRONG_REQUEST = (
    "❗️ Некорректный запрос. "
    "Отправьте просто число, сколько денег было потрачено, "
    "значение должно быть больше нуля."
)

MONEY_LEFT_HAS = "Осталось до конца месяца: {:g}"

MONEY_RAN_OUT = "Перерасход бюджета: {:g}❗️"

UPDATE_MESSAGE = "✅ Зачислено <b>{:g}</b> денег в категорию <b>{}</b>. "

CHOOSE_CATEGORY = "⬇️ Выбери категорию для траты {:g} денег"

NO_CATEGORIES = (
    "❗️ Сначала создайте хотя бы одну категорию, "
    "чтобы добавлять траты: /add_category"
)

DELETE_MESSAGE = (
    "❌ Трата на сумму <b>{:g}</b> денег в категории {} была <b>удалена</b>. "
)

MONEY_LEFT_MESSAGE = (
    "📝 Текущий месяц: {}\n" "Бюджет на месяц: {:g}\n" "Потрачено: {:g}\n"
)

MONTH_CATEGORIES_LABEL = "\nТраты за месяц по категориям:"

START_MESSAGE = (
    "📝 Теперь ты можешь вести бюджет. Просто пиши мне цифру денег, "
    "которую ты потратил и выбери нужную категорию."
)

ACTION_CANCELED = "❌ Действие отменено."

ENTER_CATEGORY_NAME = (
    "Введите название категории трат, " "которую хотите создать, для отмены /cancel"
)

CATEGORY_ADD_SUCCESS = '✅ Категория с названием "{}" была успешно добавлена!'

CATEGORY_ALREADY_EXISTS = (
    '❗️ Категория с названием "{}" уже существует. '
    "Добавьте категорию с уникальным названием или /cancel"
)

CATEGORY_NAME_TOO_LONG = (
    "❗ Вы указали слишком длинное имя для новой категории. "
    "Напишите более короткое название для категории или /cancel"
)

NO_TODAY_EXPENSES = "Сегодня еще нет трат 👀"
TODAY_EXPENSES = "💸 Сегодня было потрачено: {:g} денег."
TOO_MUCH_MONEY_BRUH = " 🗿"
IN_CATEGORIES_LABEL = "\nВ категориях:"
CATEGORY_ITEM = "- {} - {:g}"

STATISTIC_YEAR_MESSAGE = "⬇️ Выберите год, за который хотите посмотреть траты"
STATISTIC_MONTH_MESSAGE = (
    "⬇️ Выберите месяц, за который вы хотите получить отчет по тратам"
)
NO_EXPENSES = "❕ В базе данных отсутствуют траты"
PERIOD_EXPENSES = "🗓 За {} {} было потрачено: {:g} денег."

ANOTHER_USER_ACTION = "Действие от {}: {}"

# Currencies

ENTER_CURRENCY_NAME: str = (
    "Введите название добавляемой валюты, например: <b>доллары</b>, или /cancel"
)

ENTER_CURRENCY_CODE: str = (
    "Введите буквенный код валюты, например: <b>USD</b>, или /cancel"
)

VALIDATION_ERROR_CURRENCY_CODE: str = (
    "❗ Код валюты должен состоять из <b>трех букв</b>, например: USD. "
    "Введите его заново."
)
VALIDATION_ERROR_CURRENCY_NAME: str = (
    "❗ Название валюты не должно превышать {} символов. Введите название заново."
)
VALIDATION_ERROR_COUNTRY: str = (
    "❗ Название страны не должно превышать {} символов. Введите название заново."
)

ENTER_CURRENCY_COUNTRY: str = "Введите название страны валюты, или /cancel"

CURRENCY_ADD_SUCCESS: str = (
    "✅ Валюта: <b>{} ({})</b> страны: <b>{}</b> была успешно добавлена!"
)

CURRENCY_NOT_UNIQUE: str = (
    f"❗ Валюта с таким названием/кодом/страной уже существует, "
    f"попробуйте снова: {ADD_CURRENCY_COMMAND}"
)

CHOOSE_CURRENCY: str = (
    "⬇️ Выберите валюту, которую необходимо установить для траты <b>{:g}</b> денег"
)

NO_CURRENCIES: str = "❗️ Сначала добавьте хотя бы одну валюту: /add_currency"

CURRENCY_SET: str = (
    "✅ Установлена валюта <b>{} ({})</b> для траты <b>{:g}</b> "
    "денег из категории <b>{}</b>"
)
