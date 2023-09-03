from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str = 'Cheapskate'
    app_description: str = '<Application for financial control>'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'SECRET'
    month_budget: int = 1350

    class Config:
        env_prefix = 'api_'
        env_file = '.env'


settings = Settings()
