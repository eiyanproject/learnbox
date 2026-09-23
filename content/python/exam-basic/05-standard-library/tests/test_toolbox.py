import pytest

from toolbox import date_facts, find_codes, round_trip, summarise


def test_summarise():
    assert summarise([1, 2, 3, 4]) == {"mean": 2.5, "median": 2.5, "stdev": 1.118}


def test_summarise_uses_population_not_sample_stdev():
    # statistics.stdev([1, 2, 3, 4]) would be 1.291
    assert summarise([1, 2, 3, 4])["stdev"] == 1.118


def test_summarise_single_value():
    assert summarise([5]) == {"mean": 5, "median": 5, "stdev": 0.0}


def test_date_facts_midweek():
    assert date_facts("2026-09-23") == {
        "formatted": "2026/09/23",
        "weekday": 2,
        "day_of_year": 266,
        "is_weekend": False,
    }


def test_date_facts_weekend():
    facts = date_facts("2026-09-26")
    assert facts["weekday"] == 5
    assert facts["is_weekend"] is True
    assert facts["day_of_year"] == 269


def test_date_facts_leap_day():
    facts = date_facts("2024-02-29")
    assert facts["formatted"] == "2024/02/29"
    assert facts["day_of_year"] == 60


@pytest.mark.parametrize(
    "text, expected",
    [
        ("order AB123 and XY999", ["AB123", "XY999"]),
        ("none here", []),
        ("ab123 is lowercase", []),
        ("AB12 is too short", []),
    ],
)
def test_find_codes(text, expected):
    assert find_codes(text) == expected


def test_round_trip_sorts_keys():
    text, restored = round_trip({"b": 1, "a": 2})
    assert text == '{"a": 2, "b": 1}'
    assert restored == {"b": 1, "a": 2}


def test_round_trip_turns_tuples_into_lists():
    _, restored = round_trip({"point": (1, 2)})
    assert restored == {"point": [1, 2]}
