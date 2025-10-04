import json
from pathlib import Path

from fastapi import status
from pydantic import SecretStr, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.app.utils import raise_api_error
from configs.enums import APIErrorCode


class Settings(BaseSettings):
    """API settings config with environment variables."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent.parent / ".env",
        extra="allow",
    )

    app_title: str = "Cheapskate"
    app_description: str = "<Application for financial control>"
    postgres_user: str
    postgres_password: SecretStr
    db_host: str
    db_port: int

    # Google API credentials
    report_spreadsheet_id: str | None = None
    google_service_account_creds: str | None = None

    @computed_field
    @property
    def database_url(self) -> str:
        return str(
            MultiHostUrl.build(
                scheme="postgresql+asyncpg",
                username=self.postgres_user,
                password=self.postgres_password.get_secret_value(),
                host=self.db_host,
                port=self.db_port,
            )
        )

    @computed_field
    @property
    def google_service_account_info(self) -> dict[str, str]:
        if not self.google_service_account_creds:
            raise_api_error(
                error_code=APIErrorCode.NO_GOOGLE_SERVICE_CREDS,
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Не указаны данные доступа к сервисному аккаунту google",
            )
        try:
            return json.loads(self.google_service_account_creds)
        except Exception:
            raise_api_error(
                error_code=APIErrorCode.BAD_GOOGLE_SERVICE_CREDS,
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Указаны некорректные данные доступа к сервисному аккаунту google",
            )


settings = Settings()
