from datetime import datetime
from typing import Self
from uuid import uuid4

import jwt
import pytest
import pytz
from httpx import ASGITransport, AsyncClient, Auth

from api import app
from backend.app.core.config import settings
from backend.app.models.user import User


class JWTAuth(Auth):
    def __init__(self, access_token: str) -> None:
        self._access_token = access_token

    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self._access_token}"
        yield request

    @classmethod
    def get_auth_by_user(cls, user: User) -> Self:
        return cls(access_token=cls._get_access_token(user))

    @staticmethod
    def _get_access_token(user: User):
        now = datetime.now(pytz.timezone(settings.time_zone))

        payload = {
            "sub": str(user.id),
            "type": "access",
            "iat": now,
            "exp": now + settings.access_token_ttl,
            "jti": str(uuid4()),
        }

        return jwt.encode(payload, settings.secret_key.get_secret_value(), algorithm="HS256")


@pytest.fixture
async def anonymous_client(override_db):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
async def authorized_client(override_db, user: User):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        auth=JWTAuth.get_auth_by_user(user),
    ) as client:
        yield client
