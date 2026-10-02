from warmup import reveal


def test_reveals_the_welcome_message():
    assert reveal("d2VsY29tZSB0byB0aGUgbGFi") == "welcome to the lab"


def test_reveals_a_short_string():
    assert reveal("aGVsbG8=") == "hello"


def test_round_trips_any_text():
    import base64
    secret = "the quick brown fox"
    assert reveal(base64.b64encode(secret.encode()).decode()) == secret


def test_returns_a_string_not_bytes():
    assert isinstance(reveal("aGk="), str)
