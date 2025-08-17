from typing import Union
from decimal import Decimal, ROUND_HALF_UP

def to_kopecks(amount: Union[float, str, Decimal]) -> int:
    """Convert decimal amount to kopecks (integer)"""
    if isinstance(amount, str):
        amount = Decimal(amount)
    return int(Decimal(amount).quantize(Decimal('0.00')).shift(2))

def to_rub(amount: int) -> Decimal:
    """Convert kopecks to rubles (Decimal)"""
    return Decimal(amount) / Decimal(100)

def format_currency(amount: int) -> str:
    """Format kopecks as currency string"""
    rub = to_rub(amount)
    return f"{rub:.2f} RUB"
