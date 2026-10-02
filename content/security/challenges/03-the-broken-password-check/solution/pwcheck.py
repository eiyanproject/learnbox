import hashlib
import hmac
import secrets

ITERATIONS = 100_000


def make_record(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return {"salt": salt.hex(), "iterations": ITERATIONS, "hash": digest.hex()}


def check_password(attempt, record):
    salt = bytes.fromhex(record["salt"])
    digest = hashlib.pbkdf2_hmac("sha256", attempt.encode(), salt, record["iterations"])
    # compare_digest, not ==: the comparison time must not depend on how many
    # bytes matched.
    return hmac.compare_digest(digest.hex(), record["hash"])


if __name__ == "__main__":
    rec = make_record("correct horse battery staple")
    print("valid:", check_password("correct horse battery staple", rec))
    print("wrong:", check_password("guess", rec))
