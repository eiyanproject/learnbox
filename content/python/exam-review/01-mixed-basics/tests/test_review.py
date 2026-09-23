import pytest

from review import bmi_category, fizz_report, initials, normalise_name


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("  ada  LOVELACE ", "Ada Lovelace"),
        ("grace hopper", "Grace Hopper"),
        ("ALAN TURING", "Alan Turing"),
        ("", ""),
    ],
)
def test_normalise_name(raw, expected):
    assert normalise_name(raw) == expected


def test_fizz_report_first_fifteen():
    assert fizz_report(15) == [
        "1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz",
        "11", "Fizz", "13", "14", "FizzBuzz",
    ]


def test_fizz_report_returns_strings_throughout():
    assert all(isinstance(item, str) for item in fizz_report(20))


def test_fizz_report_of_zero_is_empty():
    assert fizz_report(0) == []


@pytest.mark.parametrize(
    "name, expected",
    [
        ("ada lovelace king", "A.L.K."),
        ("grace hopper", "G.H."),
        ("plato", "P."),
        ("", ""),
        ("  spaced   out  ", "S.O."),
    ],
)
def test_initials(name, expected):
    assert initials(name) == expected


@pytest.mark.parametrize(
    "weight, height, expected",
    [
        (45, 1.75, "underweight"),
        (70, 1.75, "normal"),
        (85, 1.75, "overweight"),
        (100, 1.75, "obese"),
    ],
)
def test_bmi_category(weight, height, expected):
    assert bmi_category(weight, height) == expected


def test_bmi_boundaries_are_inclusive_upwards():
    # exactly 25.0 is "overweight", not "normal"
    assert bmi_category(25.0, 1.0) == "overweight"
    assert bmi_category(18.5, 1.0) == "normal"
    assert bmi_category(30.0, 1.0) == "obese"
