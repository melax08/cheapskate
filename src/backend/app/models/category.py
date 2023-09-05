from app.core.db import Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship


class Category(Base):
    """Expenses categories."""
    name = Column(String(100), unique=True, nullable=False)
    # ToDo: подумать над параметром cascade=...
    expenses = relationship('Expense', back_populates='category')
