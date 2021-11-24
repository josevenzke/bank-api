import decimal


def is_decimal(num: str) -> bool:
    try:
        decimal.Decimal(num)
        return True
    except:
        return False
