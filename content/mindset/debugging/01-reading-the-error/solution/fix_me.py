def average(values):
    """An empty list has no average; 0 is the agreed answer here."""
    if not values:
        return 0
    return sum(values) / len(values)


def get_first_word(text):
    """No words means no first word, rather than an index error."""
    words = text.split()
    if not words:
        return ""
    return words[0]


def total_price(items):
    """Quantities may arrive as strings from input; convert before arithmetic."""
    return sum(int(quantity) * price for quantity, price in items)


def find_user(users, name):
    """The bug was a missing return: the loop found it and threw it away."""
    for user in users:
        if user == name:
            return user
    return None
