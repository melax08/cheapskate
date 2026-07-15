from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from .currency import CurrencyDB


class SettingDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    budget: Decimal
    default_currency: CurrencyDB


class DefaultCurrency(BaseModel):
    currency_id: int = Field(..., ge=0)


class Budget(BaseModel):
    budget: Decimal = Field(..., ge=0)


class SettingUpdate(BaseModel):
    budget: Decimal | None = Field(None, ge=0)
    default_currency_id: int | None = Field(None, ge=0)
