from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from backend.app.core.db import Base
from configs.constants import MAX_CATEGORY_NAME_LENGTH


class Category(Base):
    """Expenses categories."""

    name = Column(String(MAX_CATEGORY_NAME_LENGTH), unique=True, nullable=False)
    # ToDo: подумать над параметром cascade=...
    expenses = relationship("Expense", back_populates="category")
    is_visible = Column(Boolean, default=True, server_default="true", nullable=False)

    def __repr__(self):
        return f"<Category {self.name}>"
