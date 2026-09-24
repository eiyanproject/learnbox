import pytest

from fix_me import average, find_user, get_first_word, total_price


def test_average_of_values():
    assert average([1, 2, 3]) == 2


def test_average_of_empty_is_zero():
    assert average([]) == 0, "an empty list should not raise ZeroDivisionError"


def test_average_of_one():
    assert average([5]) == 5


def test_first_word():
    assert get_first_word("hello world") == "hello"


def test_first_word_of_empty_string():
    assert get_first_word("") == "", "no words means no first word"


def test_first_word_of_whitespace():
    assert get_first_word("   ") == ""


def test_total_price_with_numbers():
    assert total_price([(2, 1.5), (1, 2.0)]) == 5.0


def test_total_price_with_a_string_quantity():
    assert total_price([("2", 1.5)]) == 3.0, "input often arrives as text"


def test_total_price_of_nothing():
    assert total_price([]) == 0


def test_find_user_returns_the_match():
    assert find_user(["ada", "grace"], "grace") == "grace"


def test_find_user_returns_none_when_missing():
    assert find_user(["ada"], "bob") is None


def test_find_user_result_is_usable():
    """The original bug: the value was found and never returned."""
    assert find_user(["ada"], "ada").upper() == "ADA"
