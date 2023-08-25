import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')

MINIMUM_MONEY_TO_ADD: int = 0
BUTTON_ROW_LEN: int = 3

CATEGORIES = {
    1: 'Продукты',
    2: 'Сладкое',
    3: 'Коммуналка',
    4: 'Одежда',
    5: 'Транспорт',
    6: 'Алкоголь',
    7: 'Подписки',
    8: 'Развлечения',
    20: 'Разное'
}
API_URL = 'http://127.0.0.1:8000/api/v1/'

CATEGORY_ENDPOINT_PATH = 'category'
