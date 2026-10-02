import secrets
import random


def secure_token(n_bytes=16):
    # secrets draws from the OS CSPRNG: output nobody can predict from past
    # output. token_hex(n) returns 2*n hex characters.
    return secrets.token_hex(n_bytes)


def weak_token(seed):
    # random is reproducible from its seed. That is the flaw, not a quirk:
    # anyone who knows the seed gets the same number.
    return random.Random(seed).getrandbits(32)


def predict(seed, n):
    # The attack is nothing more than running the same generator. A server that
    # seeds predictably has handed over every token it will ever issue.
    r = random.Random(seed)
    value = None
    for _ in range(n):
        value = r.getrandbits(32)
    return value


def enough_entropy(n_bytes):
    return n_bytes * 8 >= 128


if __name__ == "__main__":
    print("secure:", secure_token())
    print("weak, seed 42:", weak_token(42))
    print("3rd token a server with seed 42 issues:", predict(42, 3))
