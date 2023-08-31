import os

from dotenv import load_dotenv

load_dotenv()

MINIMUM_MONEY_TO_ADD: int = 1
BUTTON_ROW_LEN: int = 3

API_URL = 'http://127.0.0.1:8000/api/v1/'
CATEGORY_ENDPOINT_PATH = 'category/'
EXPENSE_ADD_PATH = 'expense/'
MONEY_LEFT_PATH = 'expense/money-left'
