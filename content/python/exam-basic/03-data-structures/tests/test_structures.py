import pytest

from structures import dedupe, invert, rank_scores, set_report


@pytest.mark.parametrize(
    "values, expected",
    [
        ([1, 2, 1, 3, 2], [1, 2, 3]),
        (["b", "a", "b"], ["b", "a"]),
        ([], []),
        ([7, 7, 7], [7]),
    ],
)
def test_dedupe_preserves_first_seen_order(values, expected):
    assert dedupe(values) == expected


def test_dedupe_does_not_mutate_the_input():
    values = [1, 1, 2]
    dedupe(values)
    assert values == [1, 1, 2]


def test_invert_groups_keys_by_value():
    assert invert({"a": 1, "b": 1, "c": 2}) == {1: ["a", "b"], 2: ["c"]}


def test_invert_sorts_each_group():
    assert invert({"z": 1, "a": 1}) == {1: ["a", "z"]}


def test_invert_empty():
    assert invert({}) == {}


def test_rank_scores_orders_by_score_descending():
    assert rank_scores({"ann": 10, "bob": 30, "cat": 20}) == [
        (1, "bob", 30),
        (2, "cat", 20),
        (3, "ann", 10),
    ]


def test_rank_scores_breaks_ties_alphabetically():
    assert rank_scores({"zoe": 10, "amy": 10}) == [(1, "amy", 10), (2, "zoe", 10)]


def test_rank_scores_starts_at_one():
    assert rank_scores({"solo": 5})[0][0] == 1


def test_set_report():
    assert set_report([1, 2, 3], [3, 4]) == {
        "union": [1, 2, 3, 4],
        "common": [3],
        "only_a": [1, 2],
        "symmetric": [1, 2, 4],
    }


def test_set_report_with_no_overlap():
    result = set_report([1], [2])
    assert result["common"] == []
    assert result["symmetric"] == [1, 2]
