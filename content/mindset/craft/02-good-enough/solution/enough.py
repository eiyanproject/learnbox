def apply_discount(price, kind):
    """Two cases exist, so there are two cases here."""
    if kind == "none":
        return price
    if kind == "half":
        return round(price * 0.5, 2)
    if kind == "ten":
        return round(price * 0.9, 2)
    raise ValueError(f"unknown discount: {kind}")


KNOWN_KEYS = {"host", "port", "debug"}


def parse_config(text):
    """Forgiving about input, strict about output.

    Unknown keys are ignored rather than fatal: otherwise every new key in a
    config file becomes a breaking change for older readers.
    """
    config = {}
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if key not in KNOWN_KEYS:
            continue
        if key == "port":
            config[key] = int(value)
        elif key == "debug":
            config[key] = value.lower() in ("1", "true", "yes")
        else:
            config[key] = value
    return config


def retry(func, attempts):
    """The first success wins; the last failure is what you hear about."""
    last = None
    for _ in range(max(attempts, 1)):
        try:
            return func()
        except Exception as error:  # noqa: BLE001 - the caller decides what matters
            last = error
    raise last
