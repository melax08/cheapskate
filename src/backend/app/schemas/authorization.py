from pydantic import BaseModel


class AuthorizationFromTelegramWebApp(BaseModel):
    web_app_data: str


class AuthorizationTokens(BaseModel):
    access_token: str
    refresh_token: str


class RefreshToken(BaseModel):
    refresh_token: str
