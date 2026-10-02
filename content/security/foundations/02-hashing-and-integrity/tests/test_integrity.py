import hashlib
import hmac
from integrity import sha256_hex, tampered, crack, salted_hash, verify_hmac


def test_sha256_matches_the_library():
    assert sha256_hex(b"hello") == hashlib.sha256(b"hello").hexdigest()


def test_sha256_is_deterministic():
    assert sha256_hex(b"abc") == sha256_hex(b"abc")


def test_tampered_is_false_for_untouched_data():
    data = b"the original bytes"
    assert not tampered(data, sha256_hex(data))


def test_tampered_is_true_after_a_change():
    assert tampered(b"edited bytes", sha256_hex(b"the original bytes"))


def test_crack_finds_the_password():
    target = sha256_hex(b"password123")
    assert crack(target, [b"letmein", b"password123", b"qwerty"]) == b"password123"


def test_crack_returns_none_when_not_in_the_list():
    target = sha256_hex(b"an-uncommon-passphrase")
    assert crack(target, [b"letmein", b"password", b"qwerty"]) is None


def test_crack_returns_the_first_match():
    # Two distinct words, only the real one hashes to the target.
    target = sha256_hex(b"hunter2")
    assert crack(target, [b"wrong", b"hunter2"]) == b"hunter2"


def test_salt_changes_the_hash():
    assert salted_hash(b"pw", b"saltA") != salted_hash(b"pw", b"saltB")


def test_same_salt_and_password_is_stable():
    assert salted_hash(b"pw", b"salt") == salted_hash(b"pw", b"salt")


def test_salted_hash_resists_the_unsalted_crack():
    # The dictionary attack above cracks a bare sha256; the salted digest of
    # the same password does not appear in a table of bare hashes.
    salted = salted_hash(b"password123", b"\x9f\x1a")
    assert crack(salted, [b"password123", b"letmein"]) is None


def test_verify_hmac_accepts_a_valid_tag():
    key, msg = b"secret-key", b"transfer 100"
    tag = hmac.new(key, msg, hashlib.sha256).hexdigest()
    assert verify_hmac(key, msg, tag)


def test_verify_hmac_rejects_a_forged_tag():
    assert not verify_hmac(b"secret-key", b"transfer 100", "00" * 32)


def test_verify_hmac_rejects_the_wrong_key():
    msg = b"transfer 100"
    tag = hmac.new(b"real-key", msg, hashlib.sha256).hexdigest()
    assert not verify_hmac(b"wrong-key", msg, tag)
