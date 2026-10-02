import hashlib


def public_key(g, private, p):
    # g raised to your secret, mod p. Safe to send: recovering `private` from
    # this is the discrete-log problem, infeasible for a large prime.
    return pow(g, private, p)


def shared_secret(their_public, my_private, p):
    # (g^theirs)^mine == g^(theirs*mine) == (g^mine)^theirs mod p, so both
    # sides compute the identical number without it ever crossing the wire.
    return pow(their_public, my_private, p)


def derive_key(shared):
    # The raw integer is not a key; hashing it gives uniform key material.
    return hashlib.sha256(str(shared).encode()).hexdigest()


if __name__ == "__main__":
    p, g = 23, 5
    a, b = 6, 15
    A, B = public_key(g, a, p), public_key(g, b, p)
    ka = shared_secret(B, a, p)
    kb = shared_secret(A, b, p)
    print("Alice derives", ka, " Bob derives", kb, " match:", ka == kb)
