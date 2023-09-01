from pydantic import BaseModel, Field, field_validator

from app.core.constants import MAX_CATEGORY_LENGTH


class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=MAX_CATEGORY_LENGTH)

    @field_validator('name')
    def name_cant_be_null(cls, value: str):
        if value is None:
            raise ValueError("Name field can't be null!")
        return value


class CategoryDB(CategoryCreate):
    id: int

    class Config:
        orm_mode = True
