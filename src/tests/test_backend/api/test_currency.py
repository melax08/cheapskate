import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Currency, Setting
from tests.test_backend.factories.currency import CurrencyFactory


@pytest.mark.anyio
class TestCurrencyPublicEndpoints:
    BASE_URL = "/api/v1/currencies"

    async def test_currencies_list(
        self,
        db_session: AsyncSession,
        authorized_client: AsyncClient,
        anonymous_client: AsyncClient,
    ) -> None:
        first_currency = await CurrencyFactory.create_async(session=db_session)
        second_currency = await CurrencyFactory.create_async(session=db_session)

        anon_response = await anonymous_client.get(self.BASE_URL)
        assert anon_response.status_code == status.HTTP_401_UNAUTHORIZED

        response = await authorized_client.get(self.BASE_URL)
        assert response.status_code == status.HTTP_200_OK

        currencies_count = 2
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) == currencies_count

        assert {
            "name": first_currency.name,
            "letter_code": first_currency.letter_code,
            "country": first_currency.country,
            "id": first_currency.id,
        } in response_data

        assert {
            "name": second_currency.name,
            "letter_code": second_currency.letter_code,
            "country": second_currency.country,
            "id": second_currency.id,
        } in response_data

    async def test_currencies_detail(
        self,
        db_session: AsyncSession,
        authorized_client: AsyncClient,
        anonymous_client: AsyncClient,
        currency: Currency,
    ) -> None:
        url = f"{self.BASE_URL}/{currency.id}"

        anon_response = await anonymous_client.get(url)
        assert anon_response.status_code == status.HTTP_401_UNAUTHORIZED

        response = await authorized_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert isinstance(response_data, dict)
        assert response_data == {
            "name": currency.name,
            "letter_code": currency.letter_code,
            "country": currency.country,
            "id": currency.id,
        }

        nonexistent_currency_id = 123
        response = await authorized_client.get(f"{self.BASE_URL}/{nonexistent_currency_id}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": {"error_code": "currency_not_found", "message": "Валюта не найдена"}
        }

    async def test_currencies_create(
        self,
        db_session: AsyncSession,
        authorized_client: AsyncClient,
        anonymous_client: AsyncClient,
    ) -> None:
        data = {
            "name": "Russian ruble",
            "letter_code": "RUB",
            "country": "Russia",
        }

        currencies_count_before = await db_session.execute(
            select(func.count()).select_from(Currency)
        )
        currencies_count_before = currencies_count_before.scalar() or 0

        anon_response = await anonymous_client.post(self.BASE_URL, json=data)
        assert anon_response.status_code == status.HTTP_401_UNAUTHORIZED
        currencies_count = await db_session.execute(select(func.count()).select_from(Currency))
        assert currencies_count.scalar() == currencies_count_before

        response = await authorized_client.post(self.BASE_URL, json=data)
        assert response.status_code == status.HTTP_201_CREATED
        currencies_count = await db_session.execute(select(func.count()).select_from(Currency))
        assert currencies_count.scalar() == currencies_count_before + 1
        currency = await db_session.execute(select(Currency).where(Currency.name == data["name"]))
        currency = currency.scalars().first()
        assert currency is not None
        assert response.json() == {
            "name": currency.name,
            "letter_code": currency.letter_code,
            "country": currency.country,
            "id": currency.id,
        }

        response = await authorized_client.post(self.BASE_URL, json=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        currencies_count = await db_session.execute(select(func.count()).select_from(Currency))
        assert currencies_count.scalar() == currencies_count_before + 1
        assert response.json() == {
            "detail": {
                "error_code": "not_unique_currency_fields",
                "message": "Не уникальное название/код/страна",
            }
        }

        invalid_data = {
            "name": "American dollar",
            "letter_code": "123",  # invalid letter code
            "country": "USA",
        }
        response = await authorized_client.post(self.BASE_URL, json=invalid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        currencies_count = await db_session.execute(select(func.count()).select_from(Currency))
        assert currencies_count.scalar() == currencies_count_before + 1
        assert response.json() == {"detail": "Currency code can be only alphabetic."}

    async def test_currencies_partial_update(
        self,
        db_session: AsyncSession,
        authorized_client: AsyncClient,
        anonymous_client: AsyncClient,
        currency: Currency,
    ) -> None:
        url = f"{self.BASE_URL}/{currency.id}"
        data = {
            "name": "Russian ruble",
            "letter_code": "RUB",
            "country": "Russia",
        }

        anon_response = await anonymous_client.patch(url, json=data)
        assert anon_response.status_code == status.HTTP_401_UNAUTHORIZED

        response = await authorized_client.patch(url, json=data)
        assert response.status_code == status.HTTP_200_OK

        await db_session.refresh(currency)
        assert currency.name == data["name"]
        assert currency.letter_code == data["letter_code"]
        assert currency.country == data["country"]

        unexistent_currency_id = 123
        response = await authorized_client.patch(
            f"{self.BASE_URL}/{unexistent_currency_id}", json=data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": {"error_code": "currency_not_found", "message": "Валюта не найдена"}
        }

        second_currency = await CurrencyFactory.create_async(db_session)
        second_currency_name = second_currency.name
        url = f"{self.BASE_URL}/{second_currency.id}"

        response = await authorized_client.patch(url, json=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": {
                "error_code": "not_unique_currency_fields",
                "message": "Не уникальное название/код/страна",
            }
        }
        await db_session.refresh(second_currency)
        assert second_currency.name == second_currency_name

        data = {
            "letter_code": "123"  # incorrect
        }
        response = await authorized_client.patch(f"{self.BASE_URL}/{currency.id}", json=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Currency code can be only alphabetic."}

    async def test_currencies_delete(
        self,
        db_session: AsyncSession,
        authorized_client: AsyncClient,
        anonymous_client: AsyncClient,
        currency: Currency,
        setting: Setting,
    ) -> None:
        currency_to_delete = await CurrencyFactory.create_async(db_session)
        url = f"{self.BASE_URL}/{currency_to_delete.id}"

        anon_response = await anonymous_client.delete(url)
        assert anon_response.status_code == status.HTTP_401_UNAUTHORIZED

        response = await authorized_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        currency_db = await db_session.execute(
            select(Currency).where(Currency.id == currency_to_delete.id)
        )
        assert currency_db.scalar() is None

        response = await authorized_client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": {"error_code": "currency_not_found", "message": "Валюта не найдена"}
        }

        response = await authorized_client.delete(f"{self.BASE_URL}/{currency.id}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": {
                "error_code": "default_currency",
                "message": "Валюта используется как валюта по умолчанию в настройках",
            }
        }
