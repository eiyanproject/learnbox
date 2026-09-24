def parse_row(row):
    """["apple", "2", "1.5"] -> ("apple", 2, 1.5)

    Something here is wrong. The other two functions are correct.
    """
    name, quantity, price = row
    return (name, quantity, price)


def load(rows):
    """Skip the header, parse the rest, ignore rows that will not parse."""
    parsed = []
    for row in rows[1:]:
        try:
            parsed.append(parse_row(row))
        except ValueError:
            continue
    return parsed


def summarise(rows):
    """{"items": count, "total": sum of quantity * price}"""
    parsed = load(rows)
    return {
        "items": len(parsed),
        "total": round(sum(q * p for _, q, p in parsed), 2),
    }
