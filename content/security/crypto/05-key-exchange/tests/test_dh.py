from dh import public_key, shared_secret, derive_key


def test_small_known_values():
    # p=23, g=5, a=6, b=15 is the textbook example.
    p, g = 23, 5
    assert public_key(g, 6, p) == 8
    assert public_key(g, 15, p) == 19


def test_both_sides_agree():
    p, g = 23, 5
    a, b = 6, 15
    A, B = public_key(g, a, p), public_key(g, b, p)
    assert shared_secret(B, a, p) == shared_secret(A, b, p)


def test_agreement_on_a_larger_prime():
    p = 2147483647  # a Mersenne prime
    g = 7
    a, b = 123456, 987654
    A, B = public_key(g, a, p), public_key(g, b, p)
    assert shared_secret(B, a, p) == shared_secret(A, b, p)


def test_different_private_keys_give_different_secrets():
    p, g = 23, 5
    A = public_key(g, 6, p)
    assert shared_secret(A, 15, p) != shared_secret(A, 7, p)


def test_derive_key_is_hex_and_stable():
    k = derive_key(2)
    assert k == derive_key(2)
    assert all(c in "0123456789abcdef" for c in k)
    assert len(k) == 64


def test_derive_key_differs_by_secret():
    assert derive_key(2) != derive_key(3)


def test_the_point_both_derive_the_same_key():
    p, g = 23, 5
    a, b = 6, 15
    A, B = public_key(g, a, p), public_key(g, b, p)
    assert derive_key(shared_secret(B, a, p)) == derive_key(shared_secret(A, b, p))
