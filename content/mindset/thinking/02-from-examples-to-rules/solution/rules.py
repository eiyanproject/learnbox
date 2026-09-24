import string

ALLOWED = set(string.ascii_lowercase + string.digits + "_")


def normalise(raw):
    return raw.strip().lower()


def describe_failure(name):
    name = normalise(name)
    if len(name) < 3:
        return "too short"
    if len(name) > 16:
        return "too long"
    if any(c not in ALLOWED for c in name):
        return "invalid characters"
    if not name[0].isalpha():
        return "must start with a letter"
    if name.endswith("_"):
        return "must not end with an underscore"
    return "ok"


def is_valid_username(name):
    return describe_failure(name) == "ok"
