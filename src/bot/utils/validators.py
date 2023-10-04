from utils.constants import MAX_CATEGORY_NAME_LENGTH, MINIMUM_EXPENSE_AMOUNT


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
