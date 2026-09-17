import pytest

from errors import InsufficientFunds, parse_age, safe_divide, total_valid_prices, withdraw


def test_safe_divide():
    assert safe_divide(10, 4) == 2.5


def test_safe_divide_by_zero_returns_none():
    assert safe_divide(1, 0) is None


def test_parse_age_valid():
    assert parse_age("42") == 42
    assert parse_age("0") == 0
    assert parse_age("150") == 150


def test_parse_age_not_a_number():
    with pytest.raises(ValueError):
        parse_age("forty")
    with pytest.raises(ValueError):
        parse_age("4.5")


def test_parse_age_out_of_range():
    with pytest.raises(ValueError):
        parse_age("-1")
    with pytest.raises(ValueError):
        parse_age("151")


def test_total_valid_prices():
    assert total_valid_prices(["1.50", "abc", "2.25", "", "3"]) == (6.75, 2)
    assert total_valid_prices([]) == (0, 0)


def test_withdraw_ok():
    assert withdraw(100, 30) == 70
    assert withdraw(50, 50) == 0


def test_withdraw_too_much():
    with pytest.raises(InsufficientFunds):
        withdraw(20, 21)


def test_withdraw_non_positive():
    with pytest.raises(ValueError):
        withdraw(20, 0)
    with pytest.raises(ValueError):
        withdraw(20, -5)
