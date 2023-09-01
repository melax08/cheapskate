from sqlalchemy.orm import relationship
from sqlalchemy import Column, String

from app.core.db import Base


class Category(Base):
    """Expenses categories."""
    name = Column(String(100), unique=True, nullable=False)
    expenses = relationship('Expense', back_populates='category')  # ToDo: подумать над параметром cascade=...
