import re

LOG_LINE = re.compile(r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<level>[A-Z]+) (?P<message>.+)")


def find_hashtags(text):
    return re.findall(r"#(\w+)", text)


def parse_log_line(line):
    m = LOG_LINE.fullmatch(line.strip())
    return m.groupdict() if m else None


def is_valid_username(name):
    return re.fullmatch(r"[a-z][a-z0-9_]{2,15}", name) is not None


def normalize_phone(s):
    digits = re.sub(r"\D", "", s)
    return re.sub(r"^0", "62", digits)


def mask_emails(text):
    return re.sub(r"[\w.+-]+@([\w-]+(?:\.[\w-]+)+)", r"***@\1", text)
