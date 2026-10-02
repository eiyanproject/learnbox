import hashlib
from data import ORIGINAL, CURRENT


def find_tampered(original, current):
    pass


def extract_payload(data):
    pass


if __name__ == "__main__":
    name = find_tampered(ORIGINAL, CURRENT)
    print("tampered file:", name)
    print("hidden:", extract_payload(CURRENT[name]))
