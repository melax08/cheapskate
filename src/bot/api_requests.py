from decimal import Decimal
from http import HTTPStatus
from types import TracebackType
from typing import Optional, Type

from aiohttp import ClientSession
from aiohttp.client_exceptions import ContentTypeError
from configs.api_settings import (
    CATEGORIES_PATH,
    CURRENCY_PATH,
    EXPENSE_PATH,
    MONEY_LEFT_FULL_PATH,
    PERIOD_EXPENSE_FULL_PATH,
    SET_BUDGET_FULL_PATH,
    SET_DEFAULT_CURRENCY_FULL_PATH,
    SETTINGS_PATH,
    STATISTIC_FULL_PATH,
    TODAY_EXPENSE_FULL_PATH,
)
from yarl import URL

from .exceptions import APIError, BadRequest
from .serializers import Settings


class APIClient:
    """Client that sends async requests to REST API and returns results."""

    def __init__(self, api_url: URL, session: ClientSession):
        self._api_url = api_url
        self._client = session

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        await self._close()
        return None

    async def _close(self) -> None:
        """Close aiohttp.ClientSession."""
        return await self._client.close()

    def _make_url(self, path: str) -> URL:
        """Create full URL to the needed API endpoint."""
        return self._api_url / path

    async def _post(self, path, data):
        """Make POST-requests to the specified API path with specified request
        data."""
        async with self._client.post(self._make_url(path), json=data) as response:
            return await self._response_processing(response)

    async def _get(self, path):
        """Make GET-request to the specified API path."""
        async with self._client.get(self._make_url(path)) as response:
            return await self._response_processing(response)

    async def _delete(self, path):
        """Make DELETE-request to the specified API path."""
        async with self._client.delete(self._make_url(path)) as response:
            return await self._response_processing(response)

    async def _response_processing(self, response):
        """Check response status code and get response data."""
        await self.check_response_status_code(response)
        response_json = await response.json()
        return response_json

    @staticmethod
    async def check_response_status_code(response) -> None:
        """Check if response status code is correct."""
        if response.status == HTTPStatus.BAD_REQUEST:
            raise BadRequest
        if response.status > HTTPStatus.BAD_REQUEST:
            try:
                response_data = await response.json()
            except ContentTypeError:
                response_data = "No JSON data returned"
            raise APIError(
                f"Wrong API status code: {response.status}. "
                f"Requested URL: {response.url}. "
                f"Response data: {response_data}"
            )

    async def get_categories(self) -> list:
        """Get all expense categories."""
        categories = await self._get(CATEGORIES_PATH)
        return categories

    async def add_category(self, category_name: str):
        """Add new expense category."""
        data = {"name": category_name}
        response_data = await self._post(CATEGORIES_PATH, data)
        return response_data

    async def add_expense(self, money: str, category_id: str):
        """Add new expense."""
        data = {"category_id": category_id, "amount": money}
        response_data = await self._post(EXPENSE_PATH, data)
        return response_data

    async def delete_expense(self, expense_id: str):
        """Delete specified expense."""
        response_data = await self._delete(EXPENSE_PATH + "/" + expense_id)
        return response_data

    async def get_money_left(self):
        """Get money left for current month."""
        response_data = await self._get(MONEY_LEFT_FULL_PATH)
        return response_data

    async def get_today_expenses(self):
        """Get today expenses information."""
        response_data = await self._get(TODAY_EXPENSE_FULL_PATH)
        return response_data

    async def get_expense_periods(self):
        """Get the list of years and months with expenses."""
        response_data = await self._get(PERIOD_EXPENSE_FULL_PATH)
        return response_data

    async def get_statistic(self, year: int, month: int):
        data = {"year": year, "month": month}
        response_data = await self._post(STATISTIC_FULL_PATH, data)
        return response_data

    async def add_currency(self, name: str, letter_code: str, country: str):
        data = {
            "name": name,
            "letter_code": letter_code,
            "country": country,
        }
        response_data = await self._post(CURRENCY_PATH, data)
        return response_data

    async def get_currencies(self):
        response_data = await self._get(CURRENCY_PATH)
        return response_data

    async def set_currency(self, expense_id: int, currency_id: int):
        """Set specified currency for the specified expense."""
        data = {"currency_id": currency_id}
        response_data = await self._post(
            f"{EXPENSE_PATH}/{expense_id}/{CURRENCY_PATH}", data
        )
        return response_data

    async def get_settings(self) -> Settings:
        """Get the information about application settings."""
        response_data = await self._get(SETTINGS_PATH)
        return Settings.from_api_response(response_data)

    async def set_default_currency(self, currency_id: int) -> Settings:
        data = {"currency_id": currency_id}
        response_data = await self._post(SET_DEFAULT_CURRENCY_FULL_PATH, data)
        return Settings.from_api_response(response_data)

    async def set_budget(self, budget: Decimal | str) -> Settings:
        data = {"budget": str(budget)}
        response_data = await self._post(SET_BUDGET_FULL_PATH, data)
        return Settings.from_api_response(response_data)
