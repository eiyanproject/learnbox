def bill(lines):
    n = 0
    bad = 0
    t = 0
    for l in lines:
        p = l.split("@")
        if len(p) != 2:
            bad += 1
            continue
        q = p[0].split(" x ")
        if len(q) != 2:
            bad += 1
            continue
        try:
            a = int(q[0].strip())
            b = float(p[1].strip())
        except ValueError:
            bad += 1
            continue
        nm = q[1].strip()
        if a <= 0 or b < 0 or nm == "":
            bad += 1
            continue
        t = t + a * b
        n += 1
    return {"items": n, "skipped": bad, "subtotal": round(t, 2), "total": round(t, 2)}
