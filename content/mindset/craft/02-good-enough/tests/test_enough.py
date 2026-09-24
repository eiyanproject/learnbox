import pytest

from enough import apply_discount, parse_config, retry


def test_no_discount():
    assert apply_discount(10.00, "none") == 10.00


def test_half_discount():
    assert apply_discount(10.00, "half") == 5.00


def test_ten_percent():
    assert apply_discount(10.00, "ten") == 9.00


def test_unknown_discount_is_rejected():
    with pytest.raises(ValueError):
        apply_discount(10.00, "seventeen")


def test_config_reads_known_keys():
    config = parse_config("host=example.com\nport=8080\ndebug=true\n")
    assert config == {"host": "example.com", "port": 8080, "debug": True}


def test_config_ignores_unknown_keys():
    config = parse_config("host=a\nfuture_option=whatever\n")
    assert config == {"host": "a"}, "an unknown key should not be fatal"


def test_config_ignores_comments_and_blanks():
    config = parse_config("# a comment\n\nhost=a  # trailing\n")
    assert config == {"host": "a"}


def test_config_of_nothing():
    assert parse_config("") == {}


def test_debug_accepts_several_spellings():
    assert parse_config("debug=1")["debug"] is True
    assert parse_config("debug=yes")["debug"] is True
    assert parse_config("debug=false")["debug"] is False


def test_retry_returns_the_first_success():
    calls = []

    def works():
        calls.append(1)
        return "ok"

    assert retry(works, 3) == "ok"
    assert len(calls) == 1, "it should stop as soon as it succeeds"


def test_retry_keeps_trying_until_it_works():
    calls = []

    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise RuntimeError("not yet")
        return "ok"

    assert retry(flaky, 5) == "ok"
    assert len(calls) == 3


def test_retry_reraises_the_last_error():
    def always_fails():
        raise RuntimeError("nope")

    with pytest.raises(RuntimeError):
        retry(always_fails, 2)


def test_no_dead_code_was_left_behind():
    """Commented-out code is a question no reader can answer."""
    import enough

    source = open(enough.__file__, encoding="utf-8").read()
    assert "DiscountStrategyFactoryRegistry" not in source, (
        "the unused abstraction should be deleted, not kept"
    )
