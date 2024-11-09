from decimal import Decimal


def parse_and_sum_expenses_from_message(message: str) -> Decimal:
    """Take message like: "10 30 -23" and return the sum of these
    numbers converted to decimal."""
    return sum([Decimal(expense) for expense in message.split()])
