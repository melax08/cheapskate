from decimal import Decimal

from backend.app.api.validators import check_currency_exists
from backend.app.models import Setting
from backend.app.repositories import setting_repository
from backend.app.schemas.setting import DefaultCurrency, SettingUpdate
from backend.app.services.base import BaseService


class SettingsService(BaseService):
    """Service to manage application settings."""

    async def get_settings(self) -> Setting:
        """Get actual application settings."""
        return await setting_repository.get(self._session)

    async def set_default_currency(self, currency: DefaultCurrency) -> Setting:
        """Set a new default application currency."""
        currency = await check_currency_exists(currency.currency_id, self._session)
        settings = await setting_repository.get(self._session)
        return await setting_repository.set_default_currency(settings, currency.id, self._session)

    async def set_budget(self, budget_amount: Decimal) -> Setting:
        """Set a new monthly application budget."""
        settings = await setting_repository.get(self._session)
        return await setting_repository.set_budget(settings, budget_amount, self._session)

    async def update_settings(self, settings_data: SettingUpdate) -> Setting:
        if settings_data.default_currency_id is not None:
            await check_currency_exists(settings_data.default_currency_id, self._session)
        settings = await setting_repository.get(self._session)
        return await setting_repository.update(settings, settings_data, self._session)
