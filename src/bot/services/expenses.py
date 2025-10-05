import re
from decimal import Decimal


def parse_and_sum_expenses_from_message(message: str) -> Decimal:
    """Take message like: "10 + 30 -23" and return the sum of these numbers converted to decimal."""
    expr = message.strip()
    expr = expr.replace(",", ".")
    expr = re.sub(r"(?<=\d)\s+(?=\d)", "+", expr)
    expr = re.sub(r"\s*([+-])\s*", r"\1", expr)
    expr = expr.replace("--", "+")
    expr = expr.replace("-+", "-")
    numbers = re.findall(r"[+-]?\d+(?:\.\d+)?", expr)
    return sum(Decimal(number) for number in numbers)
