import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import User
from tests.test_backend.factories.user import UserFactory


@pytest.mark.anyio
class TestUserPublicEndpoints:
    BASE_URL = "/api/v1/users"

    async def test_users_list(
        self,
        db_session: AsyncSession,
        authorized_client: AsyncClient,
        anonymous_client: AsyncClient,
        user: User,
    ) -> None:
        another_user = await UserFactory.create_async(db_session)

        anon_response = await anonymous_client.get(self.BASE_URL)
        assert anon_response.status_code == status.HTTP_401_UNAUTHORIZED

        response = await authorized_client.get(self.BASE_URL)
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) == 2
        assert {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "telegram_username": user.telegram_username,
            "telegram_first_name": user.telegram_first_name,
            "telegram_last_name": user.telegram_last_name,
            "created_at": user.created_at.isoformat(),
        } in response_data
        assert {
            "id": another_user.id,
            "telegram_id": another_user.telegram_id,
            "telegram_username": another_user.telegram_username,
            "telegram_first_name": another_user.telegram_first_name,
            "telegram_last_name": another_user.telegram_last_name,
            "created_at": another_user.created_at.isoformat(),
        } in response_data
