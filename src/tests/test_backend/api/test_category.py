import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.category import Category
from backend.app.models.expense import Expense
from tests.test_backend.factories.category import CategoryFactory
from tests.test_backend.fixtures.expense import ExpenseFactory


@pytest.mark.anyio
class TestCategoryPublicEndpoints:
    BASE_URL = "/api/v1/categories"

    async def test_categories_list(
        self,
        db_session: AsyncSession,
        authorized_client: AsyncClient,
        anonymous_client: AsyncClient,
    ) -> None:
        category_with_expenses = await CategoryFactory.create_async(db_session)
        category_without_expenses = await CategoryFactory.create_async(db_session)
        expected_expenses_count = 2
        await ExpenseFactory.create_batch_async(
            session=db_session, size=expected_expenses_count, category=category_with_expenses
        )

        anon_response = await anonymous_client.get(self.BASE_URL)
        assert anon_response.status_code == status.HTTP_401_UNAUTHORIZED

        response = await authorized_client.get(self.BASE_URL)
        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        expected_categories_count = 2
        assert len(response_data) == expected_categories_count

        assert {
            "name": category_with_expenses.name,
            "is_visible": category_with_expenses.is_visible,
            "id": category_with_expenses.id,
            "expenses_count": expected_expenses_count,
        } in response_data

        assert {
            "name": category_without_expenses.name,
            "is_visible": category_without_expenses.is_visible,
            "id": category_without_expenses.id,
            "expenses_count": 0,
        } in response_data

    async def test_categories_detail(
        self,
        authorized_client: AsyncClient,
        anonymous_client: AsyncClient,
        category: Category,
    ) -> None:
        url = self.BASE_URL + f"/{category.id}"

        anon_response = await anonymous_client.get(url)
        assert anon_response.status_code == status.HTTP_401_UNAUTHORIZED

        response = await authorized_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        assert {
            "name": category.name,
            "is_visible": category.is_visible,
            "id": category.id,
        } == response.json()

        nonexistent_category_id = 123
        response = await authorized_client.get(self.BASE_URL + f"/{nonexistent_category_id}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": {"error_code": "category_not_found", "message": "Категория не найдена"}
        }

    async def test_categories_create(
        self,
        authorized_client: AsyncClient,
        anonymous_client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        data = {
            "name": "Test category",
            "is_visible": True,
        }

        anon_response = await anonymous_client.post(self.BASE_URL, json=data)
        assert anon_response.status_code == status.HTTP_401_UNAUTHORIZED

        response = await authorized_client.post(self.BASE_URL, json=data)
        assert response.status_code == status.HTTP_201_CREATED

        category_in_db = await db_session.execute(
            select(Category).where(Category.name == data["name"])
        )
        category = category_in_db.scalars().first()
        assert category is not None
        assert {
            "name": data["name"],
            "is_visible": data["is_visible"],
            "id": category.id,
        } == response.json()

        categories_count = await db_session.execute(select(func.count()).select_from(Category))
        categories_count = categories_count.scalar()

        response = await authorized_client.post(self.BASE_URL, json=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": {
                "error_code": "category_exists",
                "message": "Категория с таким названием уже существует",
            }
        }
        current_categories_count = await db_session.execute(
            select(func.count()).select_from(Category)
        )
        current_categories_count = current_categories_count.scalar()

        assert current_categories_count == categories_count

    async def test_categories_partial_update(
        self,
        authorized_client: AsyncClient,
        anonymous_client: AsyncClient,
        category: Category,
        db_session: AsyncSession,
    ) -> None:
        data = {
            "name": "New category name",
            "is_visible": False,
        }
        url = f"{self.BASE_URL}/{category.id}"
        old_category_name = category.name
        old_category_is_visible = category.is_visible
        categories_count = await db_session.execute(select(func.count()).select_from(Category))
        categories_count = categories_count.scalar()

        anon_response = await anonymous_client.patch(url, json=data)
        assert anon_response.status_code == status.HTTP_401_UNAUTHORIZED

        await db_session.refresh(category)
        assert category.name == old_category_name
        assert category.is_visible == old_category_is_visible
        new_categories_count = await db_session.execute(select(func.count()).select_from(Category))
        new_categories_count = new_categories_count.scalar()
        assert new_categories_count == categories_count

        response = await authorized_client.patch(url, json=data)
        assert response.status_code == status.HTTP_200_OK

        assert response.json() == {
            "id": category.id,
            "name": data["name"],
            "is_visible": data["is_visible"],
        }
        await db_session.refresh(category)
        assert category.name == data["name"]
        assert category.is_visible == data["is_visible"]

        new_categories_count = await db_session.execute(select(func.count()).select_from(Category))
        new_categories_count = new_categories_count.scalar()
        assert new_categories_count == categories_count

        second_category = await CategoryFactory.create_async(db_session)
        old_category_name = data["name"]
        data["name"] = second_category.name

        response = await authorized_client.patch(url, json=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": {
                "error_code": "category_exists",
                "message": "Категория с таким названием уже существует",
            }
        }
        await db_session.refresh(category)
        assert category.name == old_category_name

    async def test_categories_delete(
        self,
        authorized_client: AsyncClient,
        anonymous_client: AsyncClient,
        category: Category,
        db_session: AsyncSession,
    ) -> None:
        url = f"{self.BASE_URL}/{category.id}"

        anon_response = await anonymous_client.delete(url)
        assert anon_response.status_code == status.HTTP_401_UNAUTHORIZED

        category_db = await db_session.execute(select(Category).where(Category.id == category.id))
        assert category_db.scalars().first() is not None

        response = await authorized_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        category_db = await db_session.execute(select(Category).where(Category.id == category.id))
        assert category_db.scalars().first() is None

        response = await authorized_client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": {"error_code": "category_not_found", "message": "Категория не найдена"}
        }

        expense = await ExpenseFactory.create_async(db_session)
        expense_id = expense.id
        category_id = expense.category.id
        url = f"{self.BASE_URL}/{category_id}"
        response = await authorized_client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Нельзя удалить категорию с тратами"}

        expense_db = await db_session.execute(select(Expense).where(Expense.id == expense_id))
        expense_db = expense_db.scalars().first()
        assert expense_db is not None
        assert expense_db.category is not None
