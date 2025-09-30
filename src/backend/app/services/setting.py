from decimal import Decimal

from backend.app.api.validators import check_currency_exists
from backend.app.crud import setting_crud
from backend.app.schemas.setting import DefaultCurrency, SettingDB
from backend.app.services.base import BaseService


class SettingsService(BaseService):
    """Service to manage application settings."""

    async def get_settings(self) -> SettingDB:
        """Get actual application settings."""
        return await setting_crud.get(self._session)

    async def set_default_currency(self, currency: DefaultCurrency) -> SettingDB:
        """Set a new default application currency."""
        currency = await check_currency_exists(currency.currency_id, self._session)
        settings = await setting_crud.get(self._session)
        return await setting_crud.set_default_currency(settings, currency.id, self._session)

    async def set_budget(self, budget_amount: Decimal) -> SettingDB:
        """Set a new monthly application budget."""
        settings = await setting_crud.get(self._session)
        return await setting_crud.set_budget(settings, budget_amount, self._session)
