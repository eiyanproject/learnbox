import pytest
from rsa import keygen, encrypt, decrypt, sign, verify


def test_keygen_modulus():
    n, e, d = keygen(61, 53, e=17)
    assert n == 61 * 53
    assert e == 17


def test_keygen_private_exponent_is_the_inverse():
    _, e, d = keygen(61, 53, e=17)
    phi = 60 * 52
    assert (e * d) % phi == 1


def test_keygen_rejects_non_coprime_e():
    # 13 divides phi = 3120, so no inverse exists.
    with pytest.raises(ValueError):
        keygen(61, 53, e=13)


def test_encrypt_decrypt_round_trip():
    n, e, d = keygen(61, 53, e=17)
    for m in (2, 42, 65, 100, 3000):
        assert decrypt(encrypt(m, e, n), d, n) == m


def test_encrypt_actually_transforms():
    n, e, d = keygen(61, 53, e=17)
    assert encrypt(65, e, n) != 65


def test_known_vector():
    # The classic p=61, q=53, e=17, m=65 example.
    n, e, d = keygen(61, 53, e=17)
    assert encrypt(65, e, n) == 2790
    assert decrypt(2790, d, n) == 65


def test_sign_and_verify():
    n, e, d = keygen(61, 53, e=17)
    s = sign(123, d, n)
    assert verify(123, s, e, n)


def test_verify_rejects_a_tampered_message():
    n, e, d = keygen(61, 53, e=17)
    s = sign(123, d, n)
    assert not verify(124, s, e, n)


def test_verify_rejects_a_forged_signature():
    n, e, d = keygen(61, 53, e=17)
    assert not verify(123, 999, e, n)


def test_only_the_private_key_signs():
    # A signature from the right d verifies; an arbitrary number does not.
    n, e, d = keygen(61, 53, e=17)
    real = sign(50, d, n)
    assert verify(50, real, e, n)
    assert not verify(50, (real + 1) % n, e, n)
