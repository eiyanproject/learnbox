import hashlib
from pwcheck import make_record, check_password


def test_correct_password_verifies():
    rec = make_record("hunter2")
    assert check_password("hunter2", rec)


def test_wrong_password_rejected():
    rec = make_record("hunter2")
    assert not check_password("hunter3", rec)


def test_same_password_gives_different_records():
    # A per-user salt means identical passwords do not collide in storage.
    assert make_record("same")["hash"] != make_record("same")["hash"]


def test_record_carries_salt_and_iterations():
    rec = make_record("x")
    assert "salt" in rec and "iterations" in rec
    assert rec["iterations"] >= 10_000


def test_storage_is_not_a_bare_sha256():
    # The stored hash must not be a plain unsalted sha256 of the password.
    rec = make_record("password")
    assert rec["hash"] != hashlib.sha256(b"password").hexdigest()


def test_hash_matches_pbkdf2_of_the_record():
    rec = make_record("verify me")
    want = hashlib.pbkdf2_hmac("sha256", b"verify me",
                               bytes.fromhex(rec["salt"]), rec["iterations"]).hex()
    assert rec["hash"] == want
