def initials(full_name):
    return "".join(word[0] for word in full_name.split()).upper()


def is_palindrome(text):
    cleaned = "".join(ch for ch in text.lower() if ch.isalpha())
    return cleaned == cleaned[::-1]


def mask_card(number):
    return "*" * (len(number) - 4) + number[-4:]


def slugify(title):
    return "-".join(title.strip().lower().split())
