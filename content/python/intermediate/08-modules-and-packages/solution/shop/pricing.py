TAX_RATE = 0.11


def apply_discount(amount, percent):
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return amount * (100 - percent) / 100
