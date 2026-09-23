import pytest

from errors import AgeError, parse_ints, safe_divide, trace_order, validate_age


def test_safe_divide_normal():
    assert safe_divide(7, 2) == 3.5


def test_safe_divide_by_zero():
    assert safe_divide(1, 0) == "undefined"


@pytest.mark.parametrize(
    "items, expected",
    [
        (["1", "x", 2, None], [1, 2]),
        (["10", "20"], [10, 20]),
        (["nope"], []),
        ([], []),
        ([1.9], [1]),
    ],
)
def test_parse_ints_skips_what_raises(items, expected):
    assert parse_ints(items) == expected


def test_trace_order_when_raising():
    assert trace_order(True) == ["try", "except", "finally"]


def test_trace_order_when_not_raising():
    assert trace_order(False) == ["try", "else", "finally"]


def test_validate_age_returns_valid_ages():
    assert validate_age(0) == 0
    assert validate_age(42) == 42


def test_validate_age_raises_for_negative():
    with pytest.raises(AgeError) as info:
        validate_age(-1)
    assert str(info.value) == "age must not be negative"


def test_age_error_is_a_value_error():
    assert issubclass(AgeError, ValueError)


def test_existing_value_error_handlers_still_catch_it():
    with pytest.raises(ValueError):
        validate_age(-5)
