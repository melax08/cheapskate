from dotenv import load_dotenv

load_dotenv()

AMOUNT_DECIMAL_PLACES: int = 3

CATEGORIES_NUMBER_IN_ROW: int = 3

MONTH_NAME_MAP = {
    "January": "Январь",
    "February": "Февраль",
    "March": "Март",
    "April": "Апрель",
    "May": "Май",
    "June": "Июнь",
    "July": "Июль",
    "August": "Август",
    "September": "Сентябрь",
    "October": "Октябрь",
    "November": "Ноябрь",
    "December": "Декабрь",
}

# Request to API settings
REQUEST_API_TIMEOUT: int | float = 5
