import pytest

from decisions import describe_number, grade, is_leap_year, ticket_price


@pytest.mark.parametrize(
    "score, expected",
    [(100, "A"), (90, "A"), (89, "B"), (80, "B"), (79, "C"), (70, "C"), (69, "D"), (60, "D"), (59, "F"), (0, "F")],
)
def test_grade_boundaries(score, expected):
    assert grade(score) == expected


def test_leap_years():
    assert is_leap_year(2024) is True
    assert is_leap_year(2000) is True


def test_not_leap_years():
    assert is_leap_year(2023) is False
    assert is_leap_year(1900) is False


def test_free_tickets():
    assert ticket_price(2, False) == 0
    assert ticket_price(70, True) == 0
    assert ticket_price(65, False) == 0


def test_child_tickets_have_no_weekend_surcharge():
    assert ticket_price(3, False) == 8
    assert ticket_price(12, True) == 8


def test_adult_tickets():
    assert ticket_price(13, False) == 15
    assert ticket_price(40, True) == 18
    assert ticket_price(64, True) == 18


def test_describe_number():
    assert describe_number(0) == "zero"
    assert describe_number(4) == "positive even"
    assert describe_number(7) == "positive odd"
    assert describe_number(-2) == "negative even"
    assert describe_number(-9) == "negative odd"
