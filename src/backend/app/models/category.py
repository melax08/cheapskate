from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from utils.constants import MAX_CATEGORY_NAME_LENGTH

from backend.app.core.db import Base


class Category(Base):
    """Expenses categories."""

    name = Column(String(MAX_CATEGORY_NAME_LENGTH), unique=True, nullable=False)
    # ToDo: подумать над параметром cascade=...
    expenses = relationship("Expense", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"
