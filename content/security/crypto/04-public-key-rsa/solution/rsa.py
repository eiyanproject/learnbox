from math import gcd


def keygen(p, q, e=65537):
    n = p * q
    phi = (p - 1) * (q - 1)
    if gcd(e, phi) != 1:
        # Without coprimality e has no inverse mod phi, so no private key
        # exists for this e. Choosing e badly is a real keygen failure.
        raise ValueError(f"e={e} is not coprime with phi={phi}")
    d = pow(e, -1, phi)   # the modular inverse: d such that e*d == 1 (mod phi)
    return n, e, d


def encrypt(m, e, n):
    return pow(m, e, n)


def decrypt(c, d, n):
    return pow(c, d, n)


def sign(m, d, n):
    # Signing is decryption with the private key: only the holder of d can do it.
    return pow(m, d, n)


def verify(m, sig, e, n):
    # ...and verification is encryption with the public key, checking it undoes
    # the signature back to the original message.
    return pow(sig, e, n) == m


if __name__ == "__main__":
    n, e, d = keygen(61, 53, e=17)
    print("public key:", (n, e), " private d:", d)
    c = encrypt(65, e, n)
    print("65 encrypts to", c, "and back to", decrypt(c, d, n))
