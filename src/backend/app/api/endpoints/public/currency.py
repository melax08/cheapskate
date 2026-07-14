from fastapi import APIRouter, Depends, status

from backend.app.dependencies.authorization import get_current_user
from backend.app.schemas.currency import CurrencyCreate, CurrencyDB, CurrencyUpdate
from backend.app.services.currency import CurrencyService

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[CurrencyDB])
async def currencies_list(
    currency_service: CurrencyService = Depends(CurrencyService),
) -> list[CurrencyDB]:
    return await currency_service.get_all_currencies()


@router.get("/{currency_id}", response_model=CurrencyDB)
async def currencies_detail(
    currency_id: int,
    currency_service: CurrencyService = Depends(CurrencyService),
) -> CurrencyDB:
    return await currency_service.get_currency_by_id(currency_id)


@router.post("", response_model=CurrencyDB, status_code=status.HTTP_201_CREATED)
async def currencies_create(
    currency: CurrencyCreate,
    currency_service: CurrencyService = Depends(CurrencyService),
) -> CurrencyDB:
    return await currency_service.create_currency(currency)


@router.patch("/{currency_id}", response_model=CurrencyDB)
async def currencies_partial_update(
    currency_id: int,
    currency: CurrencyUpdate,
    currency_service: CurrencyService = Depends(CurrencyService),
) -> CurrencyDB:
    return await currency_service.update_currency(currency_id, currency)


@router.delete("/{currency_id}", status_code=status.HTTP_204_NO_CONTENT)
async def currencies_delete(
    currency_id: int, currency_service: CurrencyService = Depends(CurrencyService)
) -> None:
    await currency_service.delete_currency(currency_id)
