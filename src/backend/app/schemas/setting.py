from pydantic import BaseModel, Field

from .currency import CurrencyDB


class SettingDB(BaseModel):
    id: int
    budget: int
    default_currency: CurrencyDB

    class Config:
        orm_mode = True


class DefaultCurrency(BaseModel):
    currency_id: int = Field(..., ge=0)


class Budget(BaseModel):
    budget: int = Field(..., ge=0)
