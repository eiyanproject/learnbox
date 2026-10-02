import hashlib
from passwords import estimate_bits, slow_hash, constant_time_equal, is_strong


def test_empty_password_is_zero_bits():
    assert estimate_bits("") == 0.0


def test_longer_beats_more_complex():
    assert estimate_bits("correcthorsebatterystaple") > estimate_bits("P@ss1!")


def test_entropy_grows_with_length():
    assert estimate_bits("aaaaaaaa") > estimate_bits("aaaa")


def test_wider_pool_raises_entropy_at_equal_length():
    assert estimate_bits("abcdef") < estimate_bits("abcDEF")


def test_slow_hash_matches_the_library():
    want = hashlib.pbkdf2_hmac("sha256", b"pw", b"salt", 1000).hex()
    assert slow_hash(b"pw", b"salt", 1000) == want


def test_slow_hash_depends_on_salt():
    assert slow_hash(b"pw", b"a", 1000) != slow_hash(b"pw", b"b", 1000)


def test_slow_hash_depends_on_iterations():
    assert slow_hash(b"pw", b"s", 1000) != slow_hash(b"pw", b"s", 2000)


def test_slow_hash_returns_hex():
    out = slow_hash(b"pw", b"s", 100)
    assert isinstance(out, str) and all(c in "0123456789abcdef" for c in out)


def test_constant_time_equal_true_for_equal():
    assert constant_time_equal(b"token", b"token")


def test_constant_time_equal_false_for_different():
    assert not constant_time_equal(b"token", b"taken")


def test_constant_time_equal_false_for_different_lengths():
    assert not constant_time_equal(b"short", b"longer value")


def test_constant_time_equal_handles_empty():
    assert constant_time_equal(b"", b"")


def test_is_strong_accepts_a_long_passphrase():
    assert is_strong("correcthorsebatterystaple")


def test_is_strong_rejects_a_short_one():
    assert not is_strong("P@ss1!")


def test_is_strong_rejects_a_common_password():
    # Long enough on paper would still be caught by the blocklist, but this one
    # is simply common and weak.
    assert not is_strong("password")
