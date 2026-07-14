from fastapi import HTTPException, status

from backend.app.api.validators import check_currency_exists, check_currency_unique_fields
from backend.app.exceptions import ValidationError
from backend.app.repositories import currency_repository
from backend.app.schemas.currency import CurrencyCreate, CurrencyDB, CurrencyUpdate
from backend.app.services.base import BaseService


class CurrencyService(BaseService):
    async def get_all_currencies(self) -> list[CurrencyDB]:
        """Get all currencies."""
        return await currency_repository.get_multi(self._session)

    async def get_currency_by_id(self, currency_id: int) -> CurrencyDB:
        return await check_currency_exists(currency_id, self._session)

    async def create_currency(self, currency: CurrencyCreate) -> CurrencyDB:
        """Create a currency."""
        await check_currency_unique_fields(currency, self._session)
        try:
            return await currency_repository.create(currency, self._session)
        except ValidationError as error:
            raise HTTPException(
                detail=str(error), status_code=status.HTTP_400_BAD_REQUEST
            ) from error

    async def update_currency(self, currency_id: int, currency_data: CurrencyUpdate) -> CurrencyDB:
        currency = await check_currency_exists(currency_id, self._session)
        await check_currency_unique_fields(currency_data, self._session, currency_id)
        try:
            return await currency_repository.update(currency, currency_data, self._session)
        except ValidationError as error:
            raise HTTPException(
                detail=str(error), status_code=status.HTTP_400_BAD_REQUEST
            ) from error

    async def delete_currency(self, currency_id: int) -> None:
        currency_to_delete = await check_currency_exists(currency_id, self._session)
        return await currency_repository.remove(currency_to_delete, self._session)
