from app import App


def test_login_accepts_real_credentials():
    app = App()
    assert app.login("admin", "s3cret") == "admin"
    assert app.login("alice", "password1") == "alice"


def test_login_rejects_wrong_password():
    assert App().login("admin", "nope") is None


def test_login_resists_injection():
    app = App()
    assert app.login("admin' --", "x") is None
    assert app.login("' OR '1'='1' --", "x") is None


def test_render_escapes_script():
    out = App().render_message("<script>evil()</script>")
    assert "<script>" not in out
    assert "&lt;script&gt;" in out


def test_render_shows_normal_messages():
    out = App().render_message("hello everyone")
    assert "hello everyone" in out
    assert out.startswith("<li class='msg'>")


def test_read_note_allows_the_owner():
    app = App()
    assert app.read_note(1, "admin") == "launch codes"
    assert app.read_note(2, "alice") == "shopping list"


def test_read_note_blocks_other_users():
    app = App()
    assert app.read_note(1, "alice") is None
    assert app.read_note(2, "admin") is None


def test_read_note_unknown_id():
    assert App().read_note(999, "admin") is None
