import hashlib


def public_key(g, private, p):
    pass


def shared_secret(their_public, my_private, p):
    pass


def derive_key(shared):
    pass


if __name__ == "__main__":
    p, g = 23, 5
    a, b = 6, 15
    A, B = public_key(g, a, p), public_key(g, b, p)
    ka = shared_secret(B, a, p)
    kb = shared_secret(A, b, p)
    print("Alice derives", ka, " Bob derives", kb, " match:", ka == kb)
