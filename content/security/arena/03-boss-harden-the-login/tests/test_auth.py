import hashlib
import inspect

import pytest

import auth
from auth import Accounts, AuthError, LockedOut, WeakPassword

GOOD = "correct horse battery"


@pytest.fixture
def accounts():
    a = Accounts()
    a.register("ana", GOOD)
    return a


def everything_held(a):
    return repr(vars(a))


# ---- 1. storage


def test_the_password_is_not_stored(accounts):
    held = everything_held(accounts)
    assert GOOD not in held
    assert repr(GOOD.encode()) not in held


def test_it_is_not_a_bare_fast_hash(accounts):
    held = everything_held(accounts)
    for name in ("md5", "sha1", "sha256", "sha512"):
        h = hashlib.new(name, GOOD.encode())
        assert h.hexdigest() not in held, f"an unsalted {name} of the password is stored"
        assert repr(h.digest()) not in held, f"an unsalted {name} of the password is stored"


def test_the_same_password_gives_different_records(accounts):
    accounts.register("bo", GOOD)
    assert accounts.users["ana"] != accounts.users["bo"], "no salt: equal passwords are visibly equal"


def test_registering_twice_salts_afresh():
    a, b = Accounts(), Accounts()
    a.register("ana", GOOD)
    b.register("ana", GOOD)
    assert a.users["ana"] != b.users["ana"]


# ---- 2. registration


@pytest.mark.parametrize("password", ["", "short", "123456789"])
def test_weak_passwords_are_refused(password):
    a = Accounts()
    with pytest.raises(WeakPassword):
        a.register("ana", password)
    assert "ana" not in a.users


def test_ten_characters_is_enough():
    a = Accounts()
    a.register("ana", "0123456789")
    assert a.whoami(a.login("ana", "0123456789")) == "ana"


def test_a_name_cannot_be_taken_over(accounts):
    with pytest.raises(AuthError):
        accounts.register("ana", "another long password")
    assert accounts.whoami(accounts.login("ana", GOOD)) == "ana"
    with pytest.raises(AuthError):
        accounts.login("ana", "another long password")


# ---- 3. no enumeration


def test_login_works(accounts):
    assert accounts.whoami(accounts.login("ana", GOOD)) == "ana"


def test_failures_look_the_same(accounts):
    with pytest.raises(AuthError) as unknown:
        accounts.login("nobody", GOOD)
    with pytest.raises(AuthError) as wrong:
        accounts.login("ana", "not the password")
    assert str(unknown.value) == str(wrong.value) == "invalid credentials"
    assert type(unknown.value) is type(wrong.value) is AuthError


# ---- 4. constant-time comparison


def test_hashes_are_compared_in_constant_time():
    source = inspect.getsource(auth)
    assert "compare_digest" in source, "compare the hashes with hmac.compare_digest"
    assert "pbkdf2_hmac" in source, "hash with hashlib.pbkdf2_hmac"


# ---- 5. lockout


def fail(accounts, name, times):
    for _ in range(times):
        with pytest.raises(AuthError):
            accounts.login(name, "not the password")


def test_five_failures_lock_the_account(accounts):
    fail(accounts, "ana", 5)
    with pytest.raises(LockedOut):
        accounts.login("ana", GOOD)
    with pytest.raises(LockedOut):
        accounts.login("ana", "not the password")


def test_four_failures_do_not(accounts):
    fail(accounts, "ana", 4)
    assert accounts.whoami(accounts.login("ana", GOOD)) == "ana"


def test_a_success_resets_the_count(accounts):
    fail(accounts, "ana", 4)
    accounts.login("ana", GOOD)
    fail(accounts, "ana", 4)
    assert accounts.whoami(accounts.login("ana", GOOD)) == "ana"


def test_unlock(accounts):
    fail(accounts, "ana", 5)
    accounts.unlock("ana")
    assert accounts.whoami(accounts.login("ana", GOOD)) == "ana"
    fail(accounts, "ana", 5)
    with pytest.raises(LockedOut):
        accounts.login("ana", GOOD)


def test_locking_one_account_leaves_the_others(accounts):
    accounts.register("bo", "another long password")
    fail(accounts, "ana", 5)
    assert accounts.whoami(accounts.login("bo", "another long password")) == "bo"


def test_unknown_names_are_never_locked(accounts):
    for _ in range(8):
        with pytest.raises(AuthError) as err:
            accounts.login("nobody", "guess")
        assert not isinstance(err.value, LockedOut)
        assert str(err.value) == "invalid credentials"


# ---- 6. sessions


def test_tokens_are_long_random_and_never_repeat(accounts):
    tokens = {accounts.login("ana", GOOD) for _ in range(5)}
    assert len(tokens) == 5, "every login needs a new token"
    for token in tokens:
        assert len(token) >= 32
        assert "ana" not in token, "the token gives the user name away"
        int(token, 16)
    assert "secrets" in inspect.getsource(auth.Accounts.login), "use the secrets module for tokens"


def test_whoami_and_logout(accounts):
    first = accounts.login("ana", GOOD)
    second = accounts.login("ana", GOOD)
    accounts.logout(first)
    assert accounts.whoami(first) is None
    assert accounts.whoami(second) == "ana"
    assert accounts.whoami("ana-token") is None
    assert accounts.whoami("") is None


def test_logging_out_twice_is_harmless(accounts):
    token = accounts.login("ana", GOOD)
    accounts.logout(token)
    accounts.logout(token)
    accounts.logout("never issued")
