import json
from pathlib import Path

from pydantic import SecretStr, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


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
        return json.loads(self.google_service_account_creds)


settings = Settings()
