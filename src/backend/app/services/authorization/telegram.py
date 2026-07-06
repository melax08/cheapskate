import datetime as dt
import hashlib
import hmac
import json
from operator import itemgetter
from typing import Any
from urllib.parse import parse_qsl

import pytz
from fastapi import status

from backend.app.core.config import settings
from backend.app.crud import user_crud
from backend.app.schemas.authorization import AuthorizationTokens
from backend.app.services.authorization.jwt import JWTService
from backend.app.services.base import BaseService
from backend.app.utils import raise_api_error
from configs.enums import APIErrorCode


class TelegramAuthorizationService(BaseService):
    async def authorize_user_in_telegram_webapp(self, webapp_data: str) -> AuthorizationTokens:
        is_valid, user_data = self._check_webapp_signature(
            telegram_token=settings.bot_telegram_token.get_secret_value(),
            webapp_data=webapp_data,
            web_app_data_lifetime=settings.telegram_webapp_data_lifetime,
        )
        if is_valid and (
            user := await user_crud.get_by_telegram_id(user_data.get("id"), self._session)
        ):
            jwt_service = JWTService()
            return jwt_service.issue_tokens_for_user(user)

        raise_api_error(
            error_code=APIErrorCode.AUTHORIZATION_ERROR,
            message="Невалидные данные доступа",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    @staticmethod
    def _check_webapp_signature(
        telegram_token: str,
        webapp_data: str,
        web_app_data_lifetime: dt.timedelta = dt.timedelta(minutes=5),
    ) -> tuple[bool, dict[str, Any] | None]:
        try:
            parsed_data = dict(parse_qsl(webapp_data))

            if "hash" not in parsed_data:
                raise ValueError

            auth_date = dt.datetime.fromtimestamp(
                int(parsed_data.get("auth_date")), tz=pytz.timezone(settings.time_zone)
            )
            now = dt.datetime.now(pytz.timezone(settings.time_zone))
            if not now >= auth_date >= now - web_app_data_lifetime:
                raise ValueError

        except (ValueError, TypeError):
            # Init data is not a valid query string
            return False, None

        hash_ = parsed_data.pop("hash")
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(parsed_data.items(), key=itemgetter(0))
        )

        secret_key = hmac.new(
            key=b"WebAppData", msg=telegram_token.encode(), digestmod=hashlib.sha256
        )
        if (
            hmac.new(
                key=secret_key.digest(),
                msg=data_check_string.encode(),
                digestmod=hashlib.sha256,
            ).hexdigest()
            == hash_
        ):
            return True, json.loads(parsed_data.get("user"))

        return False, json.loads(parsed_data.get("user"))
