import hashlib
from math import log2

COMMON = {"password", "123456", "qwerty", "letmein", "admin", "iloveyou"}


def estimate_bits(password):
    pass


def slow_hash(password, salt, iterations):
    pass


def constant_time_equal(a, b):
    pass


def is_strong(password):
    pass


if __name__ == "__main__":
    for pw in ["P@ss1!", "qvhtzmkwbrpxlnjdafcs", "password"]:
        print(f"{pw:30} {estimate_bits(pw):6.1f} bits  strong={is_strong(pw)}")
