import hashlib
from math import log2

COMMON = {"password", "123456", "qwerty", "letmein", "admin", "iloveyou"}


def estimate_bits(password):
    if not password:
        return 0.0
    pool = 0
    if any(c.islower() for c in password):
        pool += 26
    if any(c.isupper() for c in password):
        pool += 26
    if any(c.isdigit() for c in password):
        pool += 10
    if any(not c.isalnum() for c in password):
        pool += 33  # the printable ASCII symbols, roughly
    # bits = length * log2(pool): every extra character multiplies the work,
    # which is why length beats a wider character set.
    return len(password) * log2(pool)


def slow_hash(password, salt, iterations):
    # pbkdf2 repeats the underlying hash `iterations` times. The cost is the
    # defence: it is paid once by the user and a billion times by the attacker.
    return hashlib.pbkdf2_hmac("sha256", password, salt, iterations).hex()


def constant_time_equal(a, b):
    # No `return` on the first mismatch: the loop always runs to the end, so the
    # time taken does not depend on how many leading bytes matched. (Production
    # code uses hmac.compare_digest, which is this, in C.)
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= x ^ y
    return result == 0


def is_strong(password):
    # A floor on entropy, plus an exact-match blocklist. The prose explains why
    # the entropy number alone is not enough - this is only a first gate.
    return estimate_bits(password) >= 60 and password.lower() not in COMMON


if __name__ == "__main__":
    for pw in ["P@ss1!", "correcthorsebatterystaple", "password"]:
        print(f"{pw:30} {estimate_bits(pw):6.1f} bits  strong={is_strong(pw)}")
