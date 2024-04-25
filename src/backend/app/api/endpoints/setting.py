from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.validators import check_currency_exists
from backend.app.core.db import get_async_session
from backend.app.crud import setting_crud
from backend.app.schemas.setting import Budget, DefaultCurrency, SettingDB

router = APIRouter()


@router.get("/", response_model=SettingDB)
async def get_settings(session: AsyncSession = Depends(get_async_session)):
    """Get first settings instance with all settings."""
    settings = await setting_crud.get_settings(session)
    return settings


@router.post("/set-default-currency", response_model=SettingDB)
async def set_default_currency(
    currency: DefaultCurrency, session: AsyncSession = Depends(get_async_session)
):
    """Set new default currency of application."""
    currency = await check_currency_exists(currency.currency_id, session)
    settings = await setting_crud.get_settings(session)
    settings = await setting_crud.set_default_currency(settings, currency.id, session)
    return settings


@router.post("/set-budget", response_model=SettingDB)
async def set_budget(
    budget: Budget, session: AsyncSession = Depends(get_async_session)
):
    """Set new application budget."""
    settings = await setting_crud.get_settings(session)
    settings = await setting_crud.set_budget(settings, budget.budget, session)
    return settings
