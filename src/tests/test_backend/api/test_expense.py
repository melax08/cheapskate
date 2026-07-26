from decimal import Decimal

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Category, Currency, Expense, Setting, User
from tests.test_backend.factories.expense import ExpenseFactory


@pytest.mark.anyio
class TestExpensePublicEndpoints:
    BASE_URL = "/api/v1/expenses"

    async def test_expenses_create(
        self,
        db_session: AsyncSession,
        authorized_client: AsyncClient,
        anonymous_client: AsyncClient,
        category: Category,
        currency: Currency,
        setting: Setting,
        user: User,
    ) -> None:
        data = {
            "amount": "123.45",
            "description": "Test description",
            "category_id": category.id,
            "currency_id": currency.id,
        }

        expenses_count_before = await db_session.execute(select(func.count()).select_from(Expense))
        expenses_count_before = expenses_count_before.scalar() or 0

        response = await anonymous_client.post(self.BASE_URL, json=data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        expenses_count = await db_session.execute(select(func.count()).select_from(Expense))
        assert expenses_count.scalar() == expenses_count_before

        response = await authorized_client.post(self.BASE_URL, json=data)
        assert response.status_code == status.HTTP_201_CREATED

        expenses_count = await db_session.execute(select(func.count()).select_from(Expense))
        assert expenses_count.scalar() == expenses_count_before + 1
        expense = await db_session.execute(
            select(Expense).where(Expense.description == data["description"])
        )
        expense = expense.scalars().first()
        assert expense is not None

        assert response.json() == {
            "id": expense.id,
            "description": expense.description,
            "amount": str(expense.amount),
            "category": {
                "name": category.name,
                "is_visible": category.is_visible,
                "id": category.id,
            },
            "currency": {
                "name": currency.name,
                "letter_code": currency.letter_code,
                "country": currency.country,
                "id": currency.id,
            },
            "date": expense.date.isoformat(),
            "money_left": str((setting.budget - Decimal(data["amount"])).quantize(Decimal(".001"))),
        }
        assert expense.user is user

        # Create expense without specify currency (may use default currency)
        actual_money_left = setting.budget - Decimal(data["amount"])
        data = {
            "amount": "33.1",
            "description": "Another expense",
            "category_id": category.id,
        }
        response = await authorized_client.post(self.BASE_URL, json=data)
        assert response.status_code == status.HTTP_201_CREATED
        expenses_count = await db_session.execute(select(func.count()).select_from(Expense))
        assert expenses_count.scalar() == expenses_count_before + 2
        expense = await db_session.execute(
            select(Expense).where(Expense.description == data["description"])
        )
        expense = expense.scalars().first()
        assert expense is not None
        assert response.json() == {
            "id": expense.id,
            "description": expense.description,
            "amount": str(expense.amount),
            "category": {
                "name": category.name,
                "is_visible": category.is_visible,
                "id": category.id,
            },
            "currency": {
                "name": currency.name,
                "letter_code": currency.letter_code,
                "country": currency.country,
                "id": currency.id,
            },
            "date": expense.date.isoformat(),
            "money_left": str(
                (actual_money_left - Decimal(data["amount"])).quantize(Decimal(".001"))
            ),
        }
        actual_money_left = actual_money_left - Decimal(data["amount"])

        # Create expense without specify category
        data = {
            "amount": "2",
            "description": "No category, huh",
            "currency_id": currency.id,
        }
        response = await authorized_client.post(self.BASE_URL, json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        # Money left out of budget
        data = {
            "amount": str(actual_money_left + 10000),
            "description": "Too much money waste...",
            "category_id": category.id,
            "currency_id": currency.id,
        }
        response = await authorized_client.post(self.BASE_URL, json=data)
        assert response.status_code == status.HTTP_201_CREATED

        expenses_count = await db_session.execute(select(func.count()).select_from(Expense))
        assert expenses_count.scalar() == expenses_count_before + 3
        expense = await db_session.execute(
            select(Expense).where(Expense.description == data["description"])
        )
        expense = expense.scalars().first()
        assert expense is not None
        assert response.json() == {
            "id": expense.id,
            "description": expense.description,
            "amount": str(expense.amount),
            "category": {
                "name": category.name,
                "is_visible": category.is_visible,
                "id": category.id,
            },
            "currency": {
                "name": currency.name,
                "letter_code": currency.letter_code,
                "country": currency.country,
                "id": currency.id,
            },
            "date": expense.date.isoformat(),
            "money_left": str(
                (actual_money_left - Decimal(data["amount"])).quantize(Decimal(".001"))
            ),
        }

    async def test_expenses_delete(
        self,
        db_session: AsyncSession,
        authorized_client: AsyncClient,
        anonymous_client: AsyncClient,
        setting: Setting,
        expense: Expense,
    ) -> None:
        url = f"{self.BASE_URL}/{expense.id}"
        expense_data = expense.__dict__

        anon_response = await anonymous_client.delete(url)
        assert anon_response.status_code == status.HTTP_401_UNAUTHORIZED
        expense_db = await db_session.execute(
            select(Expense).where(Expense.id == expense_data["id"])
        )
        expense_db = expense_db.scalars().first()
        assert expense_db is not None

        response = await authorized_client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "amount": str(expense_data["amount"]),
            "description": expense_data["description"],
            "id": expense_data["id"],
            "category": {
                "name": expense_data["category"].name,
                "is_visible": expense_data["category"].is_visible,
                "id": expense_data["category"].id,
            },
            "currency": {
                "name": expense_data["currency"].name,
                "letter_code": expense_data["currency"].letter_code,
                "country": expense_data["currency"].country,
                "id": expense_data["currency"].id,
            },
            "date": expense_data["date"].isoformat(),
            "money_left": str(Decimal(setting.budget).quantize(Decimal(".001"))),
        }
        expense_db = await db_session.execute(
            select(Expense).where(Expense.id == expense_data["id"])
        )
        expense_db = expense_db.scalars().first()
        assert expense_db is None

        response = await authorized_client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": {"error_code": "expense_not_found", "message": "Трата не найдена"}
        }

    async def test_expenses_detail(
        self,
        authorized_client: AsyncClient,
        anonymous_client: AsyncClient,
        expense: Expense,
    ) -> None:
        url = f"{self.BASE_URL}/{expense.id}"

        anon_response = await anonymous_client.get(url)
        assert anon_response.status_code == status.HTTP_401_UNAUTHORIZED

        response = await authorized_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "amount": str(expense.amount),
            "description": expense.description,
            "id": expense.id,
            "category": {
                "name": expense.category.name,
                "is_visible": expense.category.is_visible,
                "id": expense.category.id,
            },
            "currency": {
                "name": expense.currency.name,
                "letter_code": expense.currency.letter_code,
                "country": expense.currency.country,
                "id": expense.currency.id,
            },
            "date": expense.date.isoformat(),
        }

        nonexistent_expense_id = 123
        response = await authorized_client.get(f"{self.BASE_URL}/{nonexistent_expense_id}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": {"error_code": "expense_not_found", "message": "Трата не найдена"}
        }

    async def test_expenses_list(
        self,
        db_session: AsyncSession,
        authorized_client: AsyncClient,
        anonymous_client: AsyncClient,
    ) -> None:
        page_size = 9
        response = await authorized_client.get(f"{self.BASE_URL}?size={page_size}")
        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert len(response_data["items"]) == 0
        assert response_data["next_page"] is None
        assert response_data["total"] == 0

        total_expenses_count = 13
        expenses = await ExpenseFactory.create_batch_async(
            session=db_session, size=total_expenses_count
        )
        expense_with_highest_id = expenses[-1]
        expense_with_lowest_id = expenses[0]

        anon_response = await anonymous_client.get(self.BASE_URL)
        assert anon_response.status_code == status.HTTP_401_UNAUTHORIZED

        response = await authorized_client.get(f"{self.BASE_URL}?size={page_size}")
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert response_data["total"] == total_expenses_count
        assert len(response_data["items"]) == page_size
        expense_with_highest_id_data = response_data["items"][0]
        assert expense_with_highest_id_data == {
            "id": expense_with_highest_id.id,
            "amount": str(expense_with_highest_id.amount),
            "description": expense_with_highest_id.description,
            "category_id": expense_with_highest_id.category.id,
            "currency_id": expense_with_highest_id.currency.id,
            "date": expense_with_highest_id.date.isoformat(),
            "user_id": expense_with_highest_id.user.id,
        }

        next_page = response_data["next_page"]
        current_page = response_data["current_page_backwards"]
        response = await authorized_client.get(
            f"{self.BASE_URL}?size={page_size}&cursor={next_page}"
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["total"] == total_expenses_count
        assert len(response_data["items"]) == total_expenses_count - page_size
        assert response_data["items"][-1]["id"] == expense_with_lowest_id.id
        assert response_data["previous_page"] == current_page
        assert response_data["next_page"] is None

    async def test_expenses_partial_update(
        self,
        db_session: AsyncSession,
        authorized_client: AsyncClient,
        anonymous_client: AsyncClient,
        category: Category,
        currency: Currency,
        setting: Setting,
        user: User,
        expense: Expense,
    ) -> None:
        data = {
            "amount": "123.45",
            "description": "New test description",
            "category_id": category.id,
            "currency_id": currency.id,
        }
        expense_id = expense.id
        url = f"{self.BASE_URL}/{expense_id}"
        expense_date_before = expense.date

        anon_response = await anonymous_client.patch(url, json=data)
        assert anon_response.status_code == status.HTTP_401_UNAUTHORIZED
        await db_session.refresh(expense)
        assert expense.description != data["description"]

        unexisted_expense_id = 654
        response = await authorized_client.patch(
            f"{self.BASE_URL}/{unexisted_expense_id}", json=data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": {"error_code": "expense_not_found", "message": "Трата не найдена"}
        }
        await db_session.refresh(expense)
        assert expense.description != data["description"]

        response = await authorized_client.patch(url, json=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "amount": str(Decimal(data["amount"]).quantize(Decimal(".001"))),
            "category": {
                "id": category.id,
                "is_visible": category.is_visible,
                "name": category.name,
            },
            "currency": {
                "country": currency.country,
                "id": currency.id,
                "letter_code": currency.letter_code,
                "name": currency.name,
            },
            "date": expense_date_before.isoformat(),
            "description": data["description"],
            "id": expense_id,
        }
        await db_session.refresh(expense)
        assert expense.description == data["description"]
        assert expense.category_id == category.id
        assert expense.currency_id == currency.id
        assert expense.amount == Decimal(data["amount"])

        data = {"amount": -5}
        response = await authorized_client.patch(url, json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        unexisted_category_id = 123
        data = {"category_id": unexisted_category_id}
        response = await authorized_client.patch(url, json=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": {"error_code": "category_not_found", "message": "Категория не найдена"}
        }
        await db_session.refresh(expense)
        assert expense.category_id == category.id

        unexisted_currency_id = 321
        data = {"currency_id": unexisted_currency_id}
        response = await authorized_client.patch(url, json=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": {"error_code": "currency_not_found", "message": "Валюта не найдена"}
        }
        await db_session.refresh(expense)
        assert expense.currency_id == currency.id
