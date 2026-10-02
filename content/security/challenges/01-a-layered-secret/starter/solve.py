import base64
from data import BLOB


def crack(blob):
    # Undo base64, then find the single XOR byte, then un-reverse.
    pass


if __name__ == "__main__":
    print(crack(BLOB))
