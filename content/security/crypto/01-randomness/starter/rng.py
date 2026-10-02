import secrets
import random


def secure_token(n_bytes=16):
    pass


def weak_token(seed):
    pass


def predict(seed, n):
    pass


def enough_entropy(n_bytes):
    pass


if __name__ == "__main__":
    print("secure:", secure_token())
    print("weak, seed 42:", weak_token(42))
    print("3rd token a server with seed 42 issues:", predict(42, 3))
