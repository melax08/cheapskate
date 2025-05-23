from sqlalchemy import Column, String
from sqlalchemy.orm import relationship, validates

from backend.app.core.db import Base
from configs.constants import (
    COUNTRY_LENGTH,
    CURRENCY_LETTER_CODE_LENGTH,
    MAX_CURRENCY_NAME_LENGTH,
)


class Currency(Base):
    """Currency model."""

    name = Column(String(MAX_CURRENCY_NAME_LENGTH), nullable=False, unique=True)
    letter_code = Column(String(CURRENCY_LETTER_CODE_LENGTH), nullable=False, unique=True)
    country = Column(String(COUNTRY_LENGTH), nullable=False, unique=True)
    expenses = relationship("Expense", back_populates="currency")
    default_currency = relationship("Setting", uselist=False, back_populates="default_currency")

    def __repr__(self):
        return f"<Currency {self.name} ({self.letter_code}) from {self.country}>"

    @validates("letter_code")
    def validate_letter_code(self, key, code: str) -> str:
        if len(code) != CURRENCY_LETTER_CODE_LENGTH:
            raise ValueError(
                f"Length of currency code must be {CURRENCY_LETTER_CODE_LENGTH} symbols"
            )

        if not code.isalpha():
            raise ValueError("Currency code can be only alphabetic.")

        return code
