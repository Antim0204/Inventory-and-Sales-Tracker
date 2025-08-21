# src/utils/decimal_utils.py
from decimal import Decimal, getcontext, ROUND_HALF_UP

getcontext().prec = 28
getcontext().rounding = ROUND_HALF_UP

def to_decimal(val) -> Decimal:
    if isinstance(val, Decimal):
        return val
    return Decimal(str(val))
