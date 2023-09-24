import os
from typing import Union

from dotenv import load_dotenv

load_dotenv()

MINIMUM_MONEY_TO_ADD: Union[float, int] = 0.01
BUTTON_ROW_LEN: int = 3

API_VERSION = 'v1'
API_HOST = os.getenv('HOST_API', default='127.0.0.1')

API_URL = f'http://{API_HOST}:8000/api/{API_VERSION}/'
CATEGORY_ENDPOINT_PATH = 'category/'
EXPENSE_ADD_PATH = 'expense/'
MONEY_LEFT_PATH = 'expense/money-left'
TODAY_EXPENSES_PATH = 'expense/today'
PERIODS_PATH = 'expense/periods'
STATISTIC_PATH = 'expense/statistic'

# Auth settings:
ALLOWED_TELEGRAM_IDS = os.getenv('ALLOWED_TELEGRAM_IDS')
if ALLOWED_TELEGRAM_IDS is not None:
    ALLOWED_TELEGRAM_IDS = set(map(
        int, os.getenv('ALLOWED_TELEGRAM_IDS').split()))
