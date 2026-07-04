import datetime as dt

from sqlalchemy import BigInteger, Column, DateTime, String
from sqlalchemy.orm import relationship

from backend.app.core.db import Base


class User(Base):
    """User model."""

    created_at = Column(DateTime, default=dt.datetime.now)
    telegram_id = Column(BigInteger, nullable=False, unique=True)
    telegram_username = Column(String(32), nullable=True)
    telegram_first_name = Column(String(255), nullable=True)
    telegram_last_name = Column(String(255), nullable=True)
    expenses = relationship("Expense", back_populates="user")

    def __repr__(self) -> str:
        return "<User with telegram id: telegram_id>"
