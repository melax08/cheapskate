from typing import Union

from dotenv import load_dotenv

load_dotenv()

BUTTON_ROW_LEN: int = 3

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
REQUEST_API_TIMEOUT: Union[int, float] = 5
