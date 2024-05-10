from configs.constants import MAX_CATEGORY_NAME_LENGTH
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=MAX_CATEGORY_NAME_LENGTH)

    @field_validator("name")
    def name_cant_be_null(cls, value: str):
        if value is None:
            raise ValueError("Name field can't be null!")
        return value


class CategoryDB(CategoryCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
