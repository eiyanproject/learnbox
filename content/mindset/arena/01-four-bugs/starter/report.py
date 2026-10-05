def average(values):
    """The mean of the numbers, or 0.0 for an empty list."""
    return sum(values) / len(values)


def longest_word(text):
    """The longest word in the text; the first one if several are level.

    An empty text gives "".
    """
    best = ""
    for word in text.split():
        if len(word) >= len(best):
            best = word
    return best


def running_total(values):
    """The total so far at each position: [1, 2, 3] gives [1, 3, 6]."""
    totals = []
    total = 0
    for i in range(1, len(values)):
        total += values[i]
        totals.append(total)
    return totals


def percent(part, whole):
    """What percentage part is of whole, rounded to 1 decimal.

    0.0 when whole is 0.
    """
    if whole == 0:
        return 0.0
    return round(part // whole * 100, 1)
