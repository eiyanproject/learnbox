from math import gcd


def keygen(p, q, e=65537):
    pass


def encrypt(m, e, n):
    pass


def decrypt(c, d, n):
    pass


def sign(m, d, n):
    pass


def verify(m, sig, e, n):
    pass


if __name__ == "__main__":
    n, e, d = keygen(61, 53, e=17)
    print("public key:", (n, e), " private d:", d)
    c = encrypt(65, e, n)
    print("65 encrypts to", c, "and back to", decrypt(c, d, n))
