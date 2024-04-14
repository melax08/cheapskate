import datetime as dt

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from backend.app.core.db import Base


class Expense(Base):
    """Expenses model."""

    date = Column(DateTime, default=dt.datetime.now, index=True)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    category = relationship("Category", back_populates="expenses", lazy="joined")
    amount = Column(Float, nullable=False)
    currency_id = Column(Integer, ForeignKey("currency.id"), nullable=True)
    currency = relationship("Currency", back_populates="expenses", lazy="joined")

    def __repr__(self):
        return f"<Expense for {self.amount} money in category {self.category_id}>"
