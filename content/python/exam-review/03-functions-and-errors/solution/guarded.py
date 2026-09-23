def apply_discount(price, percent):
    if price < 0:
        raise ValueError("price must not be negative")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return round(price * (1 - percent / 100), 2)


def average(*numbers):
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)


def safe_get(mapping, keys, default=None):
    current = mapping
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def attempt(func, fallback):
    try:
        return func()
    except Exception:
        return fallback
