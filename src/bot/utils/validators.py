from configs.constants import (
    COUNTRY_LENGTH,
    CURRENCY_LETTER_CODE_LENGTH,
    MAX_CATEGORY_NAME_LENGTH,
    MAX_CURRENCY_NAME_LENGTH,
    MINIMUM_EXPENSE_AMOUNT,
)


def money_validator(money: str) -> float:
    """Validate the amount of entered money."""
    money = float(money)
    if money < MINIMUM_EXPENSE_AMOUNT:
        raise ValueError
    return money


def category_name_validator(category: str) -> None:
    """Validate category name while adding new category."""
    if len(category) > MAX_CATEGORY_NAME_LENGTH:
        raise ValueError


def currency_code_validator(currency_code: str) -> None:
    if len(currency_code) != CURRENCY_LETTER_CODE_LENGTH:
        raise ValueError


def currency_name_validator(currency_name: str) -> None:
    if len(currency_name) > MAX_CURRENCY_NAME_LENGTH:
        raise ValueError


def currency_country_validator(currency_country: str) -> None:
    if len(currency_country) > COUNTRY_LENGTH:
        raise ValueError
