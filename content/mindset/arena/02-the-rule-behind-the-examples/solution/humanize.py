UNITS = [("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]


def humanize(seconds):
    if seconds < 0:
        raise ValueError("seconds cannot be negative")
    parts = []
    for name, size in UNITS:
        count, seconds = divmod(seconds, size)
        if count:
            parts.append(f"{count}{name}")
    return " ".join(parts) or "0s"
