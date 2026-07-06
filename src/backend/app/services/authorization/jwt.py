from datetime import datetime, timedelta
from uuid import uuid4

import jwt
import pytz
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.crud.user import user_crud
from backend.app.exceptions import JWTError
from backend.app.models.user import User
from backend.app.schemas.authorization import AuthorizationTokens


class JWTService:
    def __init__(
        self,
        secret_key: str = settings.secret_key.get_secret_value(),
        access_token_ttl: timedelta = settings.access_token_ttl,
        refresh_token_ttl: timedelta = settings.refresh_token_ttl,
    ):
        self.__secret_key = secret_key
        self.__access_token_ttl = access_token_ttl
        self.__refresh_token_ttl = refresh_token_ttl

    ALGORITHM = "HS256"

    @classmethod
    def decode_token(cls, token: str) -> dict:
        try:
            return jwt.decode(
                token, settings.secret_key.get_secret_value(), algorithms=[cls.ALGORITHM]
            )
        except InvalidTokenError as error:
            raise ValueError("Invalid token") from error

    def issue_tokens_for_user(self, user: User) -> AuthorizationTokens:
        return AuthorizationTokens(
            access_token=self._create_access_token(user.id),
            refresh_token=self._create_refresh_token(user.id),
        )

    async def get_user_by_access_token(self, token: str, session: AsyncSession) -> User:
        try:
            payload = self.decode_token(token)
        except ValueError as error:
            raise JWTError("Invalid token") from error

        if payload.get("type") != "access":
            raise JWTError("Invalid token type")

        if not (user_id := payload.get("sub")):
            raise JWTError("Invalid token payload")

        if not (user := await user_crud.get(int(user_id), session)):
            raise JWTError("User not found")

        return user

    async def refresh_tokens(
        self, refresh_token: str, session: AsyncSession
    ) -> AuthorizationTokens:
        try:
            payload = self.decode_token(refresh_token)
        except ValueError as error:
            raise JWTError("Invalid refresh token") from error

        if payload.get("type") != "refresh":
            raise JWTError("Invalid token type")

        if not (user_id := payload.get("sub")):
            raise JWTError("Invalid token payload")

        if not (user := await user_crud.get(int(user_id), session)):
            raise JWTError("User not found")

        return self.issue_tokens_for_user(user)

    def _create_token(
        self,
        user_id: int,
        token_type: str,
        expires_delta: timedelta,
    ) -> str:
        now = datetime.now(pytz.timezone(settings.time_zone))

        payload = {
            "sub": str(user_id),
            "type": token_type,
            "iat": now,
            "exp": now + expires_delta,
            "jti": str(uuid4()),
        }

        return jwt.encode(payload, self.__secret_key, algorithm=self.ALGORITHM)

    def _create_access_token(self, user_id: int) -> str:
        return self._create_token(
            user_id=user_id,
            token_type="access",
            expires_delta=self.__access_token_ttl,
        )

    def _create_refresh_token(self, user_id: int) -> str:
        return self._create_token(
            user_id=user_id,
            token_type="refresh",
            expires_delta=self.__refresh_token_ttl,
        )
