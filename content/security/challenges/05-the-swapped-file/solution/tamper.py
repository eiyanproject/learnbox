import hashlib
from data import ORIGINAL, CURRENT


def find_tampered(original, current):
    # The hash is the tell: the one file whose digest moved is the swap.
    for name, data in current.items():
        if name in original:
            if hashlib.sha256(data).hexdigest() != hashlib.sha256(original[name]).hexdigest():
                return name
    return None


def extract_payload(data):
    # The PNG ends at IEND plus its 4-byte CRC; anything after was appended.
    marker = data.find(b"IEND")
    if marker == -1:
        return b""
    return data[marker + 4 + 4:]


if __name__ == "__main__":
    name = find_tampered(ORIGINAL, CURRENT)
    print("tampered file:", name)
    print("hidden:", extract_payload(CURRENT[name]))
