ACCESS_DENIED = 'Доступ запрещен 👀'

API_ERROR = (
    '‼️ Возникла внутренняя проблема при обработке запроса. '
    'Попробуйте повторить данное действие позже.'
)

WRONG_REQUEST = (
    '❗️ Некорректный запрос. '
    'Отправьте просто число, сколько денег было потрачено, '
    'значение должно быть больше нуля.'
)

MONEY_LEFT_HAS = 'Осталось до конца месяца: {:g}'

MONEY_RAN_OUT = 'Перерасход бюджета: {:g}❗️'

UPDATE_MESSAGE = '✅ Зачислено <b>{:g}</b> денег в категорию <b>{}</b>. '

CHOOSE_CATEGORY = '⬇️ Выбери категорию для траты {:g} денег'

NO_CATEGORIES = (
    '❗️ Сначала создайте хотя бы одну категорию, '
    'чтобы добавлять траты: /add_category'
)

DELETE_MESSAGE = (
    '❌ Трата на сумму <b>{:g}</b> денег в категории {} была <b>удалена</b>. '
)

MONEY_LEFT_MESSAGE = (
    '📝 Текущий месяц: {}\n'
    'Бюджет на месяц: {:g}\n'
    'Потрачено: {:g}\n'
)

MONTH_CATEGORIES_LABEL = '\nТраты за месяц по категориям:'

START_MESSAGE = (
    '📝 Теперь ты можешь вести бюджет. Просто пиши мне цифру денег, '
    'которую ты потратил и выбери нужную категорию.'
)

ACTION_CANCELED = '❌ Действие отменено.'

ENTER_CATEGORY_NAME = (
    'Введите название категории трат, '
    'которую хотите создать, для отмены /cancel'
)

CATEGORY_ADD_SUCCESS = '✅ Категория с названием "{}" была успешно добавлена!'

CATEGORY_ALREADY_EXISTS = (
    '❗️ Категория с названием "{}" уже существует. '
    'Добавьте категорию с уникальным названием или /cancel'
)

CATEGORY_NAME_TOO_LONG = (
    '❗ Вы указали слишком длинное имя для новой категории. '
    'Напишите более короткое название для категории или /cancel'
)

NO_TODAY_EXPENSES = 'Сегодня еще нет трат 👀'
TODAY_EXPENSES = '💸 Сегодня было потрачено: {:g} денег.'
TOO_MUCH_MONEY_BRUH = ' 🗿'
IN_CATEGORIES_LABEL = '\nВ категориях:'
CATEGORY_ITEM = '- {} - {:g}'

SELECT_EXPENSE_PERIOD = (
    '⬇️ Выберите период, за который хотите получить отчет по тратам'
)
PERIOD_EXPENSES = '🗓 За {} {} было потрачено: {:g} денег.'

ANOTHER_USER_ACTION = 'Действие от {}: {}'
