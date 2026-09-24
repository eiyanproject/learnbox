def line_total(quantity, price):
    return round(quantity * price, 2)


def subtotal(items):
    return round(sum(line_total(q, p) for _, q, p in items), 2)


def tax(amount, rate=0.10):
    return round(amount * rate, 2)


def total(items):
    sub = subtotal(items)
    return round(sub + tax(sub), 2)


def format_receipt(items):
    rows = [f"{name} {qty} x {price} = {line_total(qty, price):.2f}" for name, qty, price in items]
    sub = subtotal(items)
    rows.append(f"SUBTOTAL {sub:.2f}")
    rows.append(f"TAX {tax(sub):.2f}")
    rows.append(f"TOTAL {total(items):.2f}")
    return "\n".join(rows)
