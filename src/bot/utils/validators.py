from bot.constants.constants import MINIMUM_MONEY_TO_ADD


def money_validator(money: str) -> float:
    """Validate the amount of entered money."""
    money = float(money)
    if money < MINIMUM_MONEY_TO_ADD:
        raise ValueError
    return money
