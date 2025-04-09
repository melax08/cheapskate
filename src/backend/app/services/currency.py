from fastapi import HTTPException, status

from backend.app.api.validators import check_currency_unique_fields
from backend.app.crud.currency import currency_crud
from backend.app.schemas.currency import CurrencyCreate, CurrencyDB
from backend.app.services.base import BaseService


class CurrencyService(BaseService):
    async def get_all_currencies(self) -> list[CurrencyDB]:
        """Get all currencies."""
        return await currency_crud.get_multi(self._session)

    async def create_currency(self, currency: CurrencyCreate) -> CurrencyDB:
        """Create a currency."""
        await check_currency_unique_fields(currency, self._session)
        try:
            return await currency_crud.create(currency, self._session)
        # ToDo: refactor this to fix potential vulnerabilities
        except ValueError as error:
            raise HTTPException(
                detail=str(error), status_code=status.HTTP_400_BAD_REQUEST
            ) from error
