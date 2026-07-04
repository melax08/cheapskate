import datetime as dt

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    telegram_id: int
    telegram_username: str | None = Field(..., max_length=32)
    telegram_first_name: str = Field(..., max_length=255)
    telegram_last_name: str | None = Field(..., max_length=255)


class UserCreate(UserBase):
    pass


class UserDB(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: dt.datetime
