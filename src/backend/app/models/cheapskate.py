import datetime as dt

from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey

from app.core.db import Base


class Category(Base):
    """Expenses categories."""
    name = Column(String(100), unique=True, nullable=False)
    expenses = relationship('Expense')  # ToDo: подумать над параметром cascade=...


class Expense(Base):
    """Expenses model."""
    date = Column(DateTime, default=dt.datetime.now, index=True)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    amount = Column(Integer, nullable=False)
