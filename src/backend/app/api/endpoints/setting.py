from fastapi import APIRouter, Depends

from backend.app.schemas.setting import Budget, DefaultCurrency, SettingDB
from backend.app.services.setting import SettingsService

router = APIRouter()


@router.get("/", response_model=SettingDB)
async def get_settings(settings_service: SettingsService = Depends(SettingsService)) -> SettingDB:
    """Get the first settings instance with all settings."""
    return await settings_service.get_settings()


@router.post("/set-default-currency", response_model=SettingDB)
async def set_default_currency(
    currency: DefaultCurrency, settings_service: SettingsService = Depends(SettingsService)
) -> SettingDB:
    """Set new default currency of the application."""
    return await settings_service.set_default_currency(currency)


@router.post("/set-budget", response_model=SettingDB)
async def set_budget(
    budget: Budget, settings_service: SettingsService = Depends(SettingsService)
) -> SettingDB:
    """Set the new application monthly budget."""
    return await settings_service.set_budget(budget.budget)
