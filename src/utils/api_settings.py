import os

from dotenv import load_dotenv

load_dotenv()

# API settings
API_VERSION = "v1"
API_PATH = f"/api/{API_VERSION}"
API_HOST = os.getenv("HOST_API", default="127.0.0.1")
API_URL = f"http://{API_HOST}:8000{API_PATH}/"

# Root paths
CATEGORIES_PATH = "category"
EXPENSE_PATH = "expense"
CURRENCY_PATH = "currency"
SETTINGS_PATH = "settings"

# Relative paths
MONEY_LEFT_PATH = "/money_left"
TODAY_EXPENSE_PATH = "/today"
PERIOD_EXPENSE_PATH = "/period"
STATISTIC_PATH = "/statistic"
SET_DEFAULT_CURRENCY_PATH = "/set-default-currency"

# Full paths
MONEY_LEFT_FULL_PATH = EXPENSE_PATH + MONEY_LEFT_PATH
TODAY_EXPENSE_FULL_PATH = EXPENSE_PATH + TODAY_EXPENSE_PATH
PERIOD_EXPENSE_FULL_PATH = EXPENSE_PATH + PERIOD_EXPENSE_PATH
STATISTIC_FULL_PATH = EXPENSE_PATH + STATISTIC_PATH
SET_DEFAULT_CURRENCY_FULL_PATH = SETTINGS_PATH + SET_DEFAULT_CURRENCY_PATH
