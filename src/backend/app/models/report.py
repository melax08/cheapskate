import datetime

from sqlalchemy import Column, DateTime, String

from backend.app.core.db import Base


class Report(Base):
    """
    Report model.
    Collect URL to the actual expenses report in Google Spreadsheets.
    """

    spreadsheet_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime)

    def __repr__(self) -> str:
        return f"<Expenses report: {self.url}>"

    @property
    def url(self) -> str:
        return "https://docs.google.com/spreadsheets/d/" + self.spreadsheet_id
