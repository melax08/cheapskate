import datetime as dt

from pydantic import BaseModel, ConfigDict


class ReportDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: str
    updated_at: dt.datetime | None
