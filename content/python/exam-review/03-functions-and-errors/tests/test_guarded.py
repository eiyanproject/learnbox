import pytest

from guarded import apply_discount, attempt, average, safe_get


@pytest.mark.parametrize(
    "price, percent, expected",
    [(100, 10, 90.0), (100, 0, 100.0), (100, 100, 0.0), (19.99, 15, 16.99)],
)
def test_apply_discount(price, percent, expected):
    assert apply_discount(price, percent) == expected


def test_apply_discount_rejects_negative_price():
    with pytest.raises(ValueError) as info:
        apply_discount(-1, 10)
    assert str(info.value) == "price must not be negative"


@pytest.mark.parametrize("percent", [-1, 101, 250])
def test_apply_discount_rejects_bad_percent(percent):
    with pytest.raises(ValueError) as info:
        apply_discount(100, percent)
    assert str(info.value) == "percent must be between 0 and 100"


def test_average():
    assert average(1, 2, 3) == 2.0
    assert average(10) == 10.0


def test_average_of_nothing_does_not_raise():
    assert average() == 0.0


def test_safe_get_walks_nested_dicts():
    data = {"a": {"b": {"c": 42}}}
    assert safe_get(data, ["a", "b", "c"]) == 42


def test_safe_get_returns_intermediate_dicts():
    data = {"a": {"b": 1}}
    assert safe_get(data, ["a"]) == {"b": 1}


@pytest.mark.parametrize(
    "keys",
    [["a", "missing"], ["nope"], ["a", "b", "c", "too", "deep"]],
)
def test_safe_get_missing_returns_default(keys):
    assert safe_get({"a": {"b": 1}}, keys, default="gone") == "gone"


def test_safe_get_stops_when_the_value_is_not_a_dict():
    assert safe_get({"a": 5}, ["a", "b"], default=None) is None


def test_safe_get_with_no_keys_returns_the_mapping():
    data = {"a": 1}
    assert safe_get(data, []) == data


def test_attempt_returns_the_result_when_it_works():
    assert attempt(lambda: 1 + 1, "failed") == 2


def test_attempt_returns_the_fallback_on_failure():
    def boom():
        raise RuntimeError("nope")

    assert attempt(boom, "failed") == "failed"


def test_attempt_catches_any_exception_class():
    assert attempt(lambda: 1 / 0, -1) == -1
    assert attempt(lambda: {}["missing"], -1) == -1
