from injection import make_db, login, injection_payload, safe_login


def test_the_payload_bypasses_the_vulnerable_login():
    db = make_db()
    user, pw = injection_payload()
    assert login(db, user, pw) == "admin"


def test_the_payload_does_not_use_the_real_password():
    # Whatever the payload is, it must not simply be the correct credentials.
    user, pw = injection_payload()
    assert pw != "s3cret"


def test_safe_login_accepts_correct_credentials():
    db = make_db()
    assert safe_login(db, "admin", "s3cret") == "admin"
    assert safe_login(db, "alice", "password1") == "alice"


def test_safe_login_rejects_a_wrong_password():
    db = make_db()
    assert safe_login(db, "admin", "wrong") is None


def test_safe_login_rejects_an_unknown_user():
    db = make_db()
    assert safe_login(db, "nobody", "x") is None


def test_safe_login_defeats_the_injection():
    db = make_db()
    user, pw = injection_payload()
    assert safe_login(db, user, pw) is None


def test_safe_login_defeats_the_classic_or_payload():
    db = make_db()
    assert safe_login(db, "' OR '1'='1' --", "x") is None
