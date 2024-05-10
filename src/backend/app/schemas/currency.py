from pydantic import BaseModel, ConfigDict, Field, field_validator
from utils.constants import (
    COUNTRY_LENGTH,
    CURRENCY_LETTER_CODE_LENGTH,
    MAX_CURRENCY_NAME_LENGTH,
)


class CurrencyCreate(BaseModel):
    name: str = Field(..., max_length=MAX_CURRENCY_NAME_LENGTH)
    letter_code: str = Field(
        ...,
        min_length=CURRENCY_LETTER_CODE_LENGTH,
        max_lenght=CURRENCY_LETTER_CODE_LENGTH,
    )
    country: str = Field(..., max_length=COUNTRY_LENGTH)

    @field_validator("name")
    def name_cant_be_null(cls, value: str):
        if value is None:
            raise ValueError("Name field can't be null!")
        return value


class CurrencyDB(CurrencyCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CurrencySet(BaseModel):
    currency_id: int
