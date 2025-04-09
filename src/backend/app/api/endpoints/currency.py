from fastapi import APIRouter, Depends

from backend.app.schemas.currency import CurrencyCreate, CurrencyDB
from backend.app.services.currency import CurrencyService

router = APIRouter()


@router.get("/", response_model=list[CurrencyDB])
async def get_all_currencies(
    currency_service: CurrencyService = Depends(CurrencyService),
) -> list[CurrencyDB]:
    """Gets the all currencies."""
    return await currency_service.get_all_currencies()


@router.post("/", response_model=CurrencyDB)
async def create_currency(
    currency: CurrencyCreate, currency_service: CurrencyService = Depends(CurrencyService)
) -> CurrencyDB:
    """Create a currency."""
    return await currency_service.create_currency(currency)
