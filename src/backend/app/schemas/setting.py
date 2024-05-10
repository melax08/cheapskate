from pydantic import BaseModel, ConfigDict, Field

from .currency import CurrencyDB


class SettingDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    budget: int
    default_currency: CurrencyDB


class DefaultCurrency(BaseModel):
    currency_id: int = Field(..., ge=0)


class Budget(BaseModel):
    budget: int = Field(..., ge=0)
