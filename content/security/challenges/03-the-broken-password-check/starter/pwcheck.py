import hashlib
import hmac
import secrets

ITERATIONS = 100_000


def make_record(password):
    # A salted, slow record: {"salt": hex, "iterations": int, "hash": hex}.
    pass


def check_password(attempt, record):
    # Recompute and compare in constant time.
    pass


if __name__ == "__main__":
    rec = make_record("correct horse battery staple")
    print("valid:", check_password("correct horse battery staple", rec))
    print("wrong:", check_password("guess", rec))
