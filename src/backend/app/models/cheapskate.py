from sqlalchemy import Column, String

from app.core.db import Base


class Category(Base):
    """Spending categories."""
    name = Column(String(100), unique=True, nullable=False)
