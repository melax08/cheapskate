from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_async_session
from backend.app.dependencies.authorization import get_current_user
from backend.app.exceptions import JWTError
from backend.app.models.user import User
from backend.app.schemas.authorization import (
    AuthorizationFromTelegramWebApp,
    AuthorizationTokens,
    RefreshToken,
)
from backend.app.schemas.user import UserDB
from backend.app.services.authorization.jwt import JWTService
from backend.app.services.authorization.telegram import TelegramAuthorizationService

router = APIRouter()


@router.post("/telegram-web-app", response_model=AuthorizationTokens)
async def authorize_telegram_web_app(
    authorization_web_app: AuthorizationFromTelegramWebApp,
    telegram_authorization_service: TelegramAuthorizationService = Depends(
        TelegramAuthorizationService
    ),
) -> AuthorizationTokens:
    return await telegram_authorization_service.authorize_user_in_telegram_webapp(
        authorization_web_app.web_app_data
    )


@router.get("/me", response_model=UserDB)
async def get_me(current_user: User = Depends(get_current_user)) -> UserDB:
    return current_user


@router.post("/refresh-tokens", response_model=AuthorizationTokens)
async def refresh_tokens(
    refresh_token: RefreshToken, session: AsyncSession = Depends(get_async_session)
):
    service = JWTService()
    try:
        return await service.refresh_tokens(refresh_token.refresh_token, session)
    except JWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error
