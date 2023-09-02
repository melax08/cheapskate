import os

from dotenv import load_dotenv

load_dotenv()

MINIMUM_MONEY_TO_ADD: int = 1
BUTTON_ROW_LEN: int = 3

API_VERSION = 'v1'
API_HOST = os.getenv('HOST_API', default='127.0.0.1')

API_URL = f'http://{API_HOST}:8000/api/{API_VERSION}/'
CATEGORY_ENDPOINT_PATH = 'category/'
EXPENSE_ADD_PATH = 'expense/'
MONEY_LEFT_PATH = 'expense/money-left'
