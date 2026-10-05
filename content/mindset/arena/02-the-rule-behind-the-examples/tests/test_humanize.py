import pytest

from humanize import humanize


@pytest.mark.parametrize(
    "seconds, text",
    [
        (0, "0s"),
        (59, "59s"),
        (60, "1m"),
        (61, "1m 1s"),
        (3600, "1h"),
        (3725, "1h 2m 5s"),
        (86400, "1d"),
        (90000, "1d 1h"),
        (172805, "2d 5s"),
    ],
)
def test_the_examples(seconds, text):
    assert humanize(seconds) == text


@pytest.mark.parametrize(
    "seconds, text",
    [
        (1, "1s"),
        (119, "1m 59s"),
        (3599, "59m 59s"),
        (3601, "1h 1s"),
        (7200, "2h"),
        (86399, "23h 59m 59s"),
        (86460, "1d 1m"),
        (90061, "1d 1h 1m 1s"),
        (8640000, "100d"),
    ],
)
def test_the_rule_holds_beyond_the_examples(seconds, text):
    assert humanize(seconds) == text


def test_negative_is_a_mistake():
    with pytest.raises(ValueError):
        humanize(-1)
