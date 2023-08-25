from yarl import URL
from types import TracebackType
from typing import Optional, Type

import aiohttp

from .constants import API_URL, CATEGORY_ENDPOINT_PATH


class ApiClient:
    """
    - Open session;
    - Request exceptions;
    - get_categories method;
    - send_expense method;
    - delete_expense method;
    - month_statistic;
    - etc;
    """

    def __init__(self, api_url: URL):
        self._api_url = api_url
        self._client = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        await self.close()
        return None

    async def close(self) -> None:
        return await self._client.close()

    def _make_url(self, path: str) -> URL:
        return self._api_url / path

    async def _post(self, path, data):
        async with self._client.post(self._make_url(path), json=data) as response:
            response_json = await response.json()
            return response_json

    async def _get(self, path):
        async with self._client.get(self._make_url(path)) as response:
            response_json = await response.json()
            return response_json

    async def get_categories(self):
        categories = await self._get(CATEGORY_ENDPOINT_PATH)
        return categories


client = ApiClient(URL(API_URL))


async def send_expense_to_api(money: str, category_id: str) -> tuple[int, int]:
    print(f'ЗАГЛУШКА. Отправлено {money} денег по категории {category_id}')
    return 100500 - int(money), 5


async def delete_expense_request(expense_id: str):
    print(f'ЗАГЛУШКА. Удален, а может и не удален расход с id {expense_id} на сумму ...')