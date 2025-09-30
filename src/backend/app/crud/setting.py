from decimal import Decimal

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Currency, Setting

from .base import SingletonCRUDBase


class CRUDSetting(SingletonCRUDBase):
    """Class with DB CRUD operations for `Setting` model."""

    async def get_default_currency(self, session: AsyncSession) -> Currency:
        """Get the instance of default application currency."""
        settings_instance = await self.get(session)
        return settings_instance.default_currency

    async def get_budget(self, session: AsyncSession) -> Decimal:
        """Get current budget."""
        settings_instance = await self.get(session)
        return settings_instance.budget

    async def set_default_currency(
        self, setting: Setting, currency_id: int, session: AsyncSession
    ) -> Setting:
        """Set currency as default application currency."""
        await session.execute(
            update(self.model)
            .where(self.model.id == setting.id)
            .values(default_currency_id=currency_id)
        )
        await session.commit()
        await session.refresh(setting)
        return setting

    async def set_budget(self, setting: Setting, budget: int, session: AsyncSession) -> Setting:
        """Set application budget."""
        await session.execute(
            update(self.model).where(self.model.id == setting.id).values(budget=budget)
        )
        await session.commit()
        await session.refresh(setting)
        return setting


setting_crud = CRUDSetting(Setting)
