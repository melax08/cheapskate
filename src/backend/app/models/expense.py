import datetime as dt

from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, Integer, ForeignKey, Float

from app.core.db import Base


class Expense(Base):
    """Expenses model."""
    date = Column(DateTime, default=dt.datetime.now, index=True)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    category = relationship('Category', back_populates='expenses')
    amount = Column(Float, nullable=False)
