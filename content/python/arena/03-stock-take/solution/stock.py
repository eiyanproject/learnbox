def stock_take(lines):
    quantities = {}
    total = 0.0
    skipped = []
    for number, line in enumerate(lines, start=1):
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        parts = [part.strip() for part in text.split(",")]
        try:
            if len(parts) != 3 or not parts[0]:
                raise ValueError("bad shape")
            name = parts[0].lower()
            quantity = int(parts[1])
            price = float(parts[2])
            if quantity < 0 or price < 0:
                raise ValueError("negative")
        except ValueError:
            skipped.append(number)
            continue
        quantities[name] = quantities.get(name, 0) + quantity
        total += quantity * price
    return quantities, round(total, 2), skipped
