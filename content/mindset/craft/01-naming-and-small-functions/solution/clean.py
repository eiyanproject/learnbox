def is_expired(days_until_expiry):
    return days_until_expiry < 0


def is_expiring_soon(days_until_expiry, warning_days):
    return not is_expired(days_until_expiry) and days_until_expiry < warning_days


def categorise(days_until_expiry, warning_days):
    if is_expired(days_until_expiry):
        return "expired"
    if is_expiring_soon(days_until_expiry, warning_days):
        return "expiring soon"
    return "fresh"
