import os
from typing import Union

from dotenv import load_dotenv

load_dotenv()

# Bot settings
TOKEN = os.getenv("TOKEN")
BUTTON_ROW_LEN: int = 3
ECHO_MESSAGES = int(os.getenv('ECHO_MESSAGES', default=1))

# Auth settings:
ALLOWED_TELEGRAM_IDS = os.getenv('ALLOWED_TELEGRAM_IDS')
if ALLOWED_TELEGRAM_IDS is not None:
    ALLOWED_TELEGRAM_IDS = set(map(
        int, os.getenv('ALLOWED_TELEGRAM_IDS').split()))

# Request to API settings
REQUEST_API_TIMEOUT: Union[int, float] = 5
