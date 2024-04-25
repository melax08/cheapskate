from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from backend.app.core.db import Base


class Setting(Base):
    """System settings."""

    # ToDo: only positive
    budget = Column(Integer, nullable=False)
    default_currency_id = Column(Integer, ForeignKey("currency.id"), nullable=True)
    default_currency = relationship(
        "Currency", back_populates="default_currency", lazy="joined"
    )

    def __repr__(self):
        return (
            f"<Setting instance. Budget: {self.budget}. "
            f"Currency: {self.default_currency_id}>"
        )
