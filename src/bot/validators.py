from .constants import MINIMUM_MONEY_TO_ADD


def money_validator(money: str):
    money = int(money)
    if money <= MINIMUM_MONEY_TO_ADD:
        raise ValueError
    return money
