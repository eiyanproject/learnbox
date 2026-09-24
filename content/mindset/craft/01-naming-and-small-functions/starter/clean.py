# Correct, and unreadable. Rewrite with names that explain themselves.
# The tests call is_expired, is_expiring_soon and categorise.


def f(d, t):
    if d < 0:
        return "e"
    elif d < t:
        return "s"
    return "f"
