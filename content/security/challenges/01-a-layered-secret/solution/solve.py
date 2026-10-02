import base64
from data import BLOB


def crack(blob):
    raw = base64.b64decode(blob)
    for key in range(256):
        candidate = bytes(b ^ key for b in raw)[::-1]
        try:
            text = candidate.decode()
        except UnicodeDecodeError:
            continue
        if text.startswith("flag{") and text.endswith("}"):
            return text
    return None


if __name__ == "__main__":
    print(crack(BLOB))
