import hashlib
import hmac


def sha256_hex(data):
    pass


def tampered(data, expected_hex):
    pass


def crack(target_hex, words):
    pass


def salted_hash(password, salt):
    pass


def verify_hmac(key, message, tag_hex):
    pass


if __name__ == "__main__":
    h = sha256_hex(b"password123")
    print("stolen hash:", h)
    print("cracked to:", crack(h, [b"letmein", b"password123", b"qwerty"]))
