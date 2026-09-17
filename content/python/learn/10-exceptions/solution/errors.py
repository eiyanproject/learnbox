class InsufficientFunds(Exception):
    pass


def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None


def parse_age(text):
    try:
        age = int(text)
    except ValueError:
        raise ValueError(f"not a whole number: {text!r}")
    if not 0 <= age <= 150:
        raise ValueError(f"age out of range: {age}")
    return age


def total_valid_prices(items):
    total = 0.0
    skipped = 0
    for item in items:
        try:
            total += float(item)
        except (ValueError, TypeError):
            skipped += 1
    return round(total, 2), skipped


def withdraw(balance, amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
    if amount > balance:
        raise InsufficientFunds(f"cannot withdraw {amount} from {balance}")
    return balance - amount
