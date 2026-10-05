def parse_line(line):
    parts = line.split("@")
    if len(parts) != 2:
        raise ValueError(f"expected one @ in {line!r}")
    left = parts[0].split(" x ")
    if len(left) != 2:
        raise ValueError(f"expected 'qty x name' in {line!r}")
    qty = int(left[0].strip())
    price = float(parts[1].strip())
    name = left[1].strip()
    if qty <= 0 or price < 0 or name == "":
        raise ValueError(f"bad values in {line!r}")
    return {"qty": qty, "name": name, "price": price}


def line_total(item):
    return item["qty"] * item["price"]


def subtotal(items):
    return round(sum(line_total(item) for item in items), 2)


def discount(amount, code):
    if code is None:
        return 0.0
    if code == "TEN":
        return round(amount * 0.10, 2)
    if code == "FIVER":
        return round(min(5.0, amount), 2)
    raise ValueError(f"unknown code {code!r}")


def bill(lines, code=None):
    items = []
    skipped = 0
    for line in lines:
        try:
            items.append(parse_line(line))
        except ValueError:
            skipped += 1
    before = subtotal(items)
    off = discount(before, code)
    return {
        "items": len(items),
        "skipped": skipped,
        "subtotal": before,
        "discount": off,
        "total": round(before - off, 2),
    }
