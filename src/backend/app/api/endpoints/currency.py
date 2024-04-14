from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_async_session
from backend.app.crud import currency_crud
from backend.app.schemas.currency import CurrencyCreate, CurrencyDB

router = APIRouter()


@router.get("/", response_model=list[CurrencyDB])
async def get_all_currencies(session: AsyncSession = Depends(get_async_session)):
    """Gets the all currencies."""
    currencies = await currency_crud.get_multi(session)
    return currencies


@router.post("/", response_model=CurrencyDB)
async def create_currency(
    category: CurrencyCreate, session: AsyncSession = Depends(get_async_session)
):
    try:
        new_currency = await currency_crud.create(category, session)
    # ToDo: при таком подходе айдишник постоянно увеличивается при фейле
    except IntegrityError as error:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Not unique name/letter_code/country",
        ) from error
    return new_currency
