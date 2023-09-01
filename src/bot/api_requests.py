from yarl import URL
from types import TracebackType
from typing import Optional, Type

import aiohttp

from bot.constants.constants import (
    API_URL,
    CATEGORY_ENDPOINT_PATH,
    EXPENSE_ADD_PATH,
    MONEY_LEFT_PATH
)


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

    async def _delete(self, path):
        async with self._client.delete(self._make_url(path)) as response:
            response_json = await response.json()
            return response_json

    async def get_categories(self) -> list:
        categories = await self._get(CATEGORY_ENDPOINT_PATH)
        return categories

    async def send_expense(self, money: str, category_id: str):
        data = {
            'category_id': category_id,
            'amount': money
        }
        response_data = await self._post(EXPENSE_ADD_PATH, data)
        return response_data

    async def delete_expense(self, expense_id: str):
        response_data = await self._delete(EXPENSE_ADD_PATH + expense_id)
        return response_data

    async def get_money_left(self):
        response_data = await self._get(MONEY_LEFT_PATH)
        return response_data


client = ApiClient(URL(API_URL))
