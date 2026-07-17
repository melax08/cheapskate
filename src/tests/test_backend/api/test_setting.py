import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_backend.factories.currency import CurrencyFactory
from tests.test_backend.fixtures.setting import Setting


@pytest.mark.anyio
class TestSettingPublicEndpoints:
    BASE_URL = "/api/v1/settings"

    async def test_get_settings(
        self,
        authorized_client: AsyncClient,
        anonymous_client: AsyncClient,
        setting: Setting,
    ) -> None:
        anon_response = await anonymous_client.get(self.BASE_URL)
        assert anon_response.status_code == status.HTTP_401_UNAUTHORIZED

        response = await authorized_client.get(self.BASE_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": setting.id,
            "budget": str(setting.budget),
            "default_currency": {
                "country": setting.default_currency.country,
                "id": setting.default_currency.id,
                "letter_code": setting.default_currency.letter_code,
                "name": setting.default_currency.name,
            },
        }

    async def test_settings_partial_update(
        self,
        db_session: AsyncSession,
        authorized_client: AsyncClient,
        anonymous_client: AsyncClient,
        setting: Setting,
    ) -> None:
        new_currency = await CurrencyFactory.create_async(db_session)
        old_budget = setting.budget
        old_default_currency = setting.default_currency
        data = {"budget": 15000, "default_currency_id": new_currency.id}

        anon_response = await anonymous_client.patch(self.BASE_URL, json=data)
        assert anon_response.status_code == status.HTTP_401_UNAUTHORIZED
        await db_session.refresh(setting)
        assert setting.budget == old_budget
        assert setting.default_currency == old_default_currency

        response = await authorized_client.patch(self.BASE_URL, json=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": setting.id,
            "budget": f"{data['budget']:.3f}",
            "default_currency": {
                "country": new_currency.country,
                "id": new_currency.id,
                "letter_code": new_currency.letter_code,
                "name": new_currency.name,
            },
        }
        await db_session.refresh(setting)
        assert setting.budget == data["budget"]
        assert setting.default_currency == new_currency
