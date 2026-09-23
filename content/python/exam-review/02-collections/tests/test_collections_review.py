import pytest

from collections_review import common_items, group_by_length, transpose, word_frequency


def test_word_frequency_counts():
    assert word_frequency("the cat the dog") == {"the": 2, "cat": 1, "dog": 1}


def test_word_frequency_is_case_insensitive():
    assert word_frequency("The the THE") == {"the": 3}


def test_word_frequency_ignores_extra_whitespace():
    assert word_frequency("  a   b  ") == {"a": 1, "b": 1}


def test_word_frequency_empty():
    assert word_frequency("") == {}


def test_group_by_length():
    assert group_by_length(["cat", "ox", "dog", "at"]) == {3: ["cat", "dog"], 2: ["at", "ox"]}


def test_group_by_length_sorts_each_bucket():
    assert group_by_length(["zebra", "apple"])[5] == ["apple", "zebra"]


def test_group_by_length_empty():
    assert group_by_length([]) == {}


@pytest.mark.parametrize(
    "matrix, expected",
    [
        ([[1, 2, 3], [4, 5, 6]], [[1, 4], [2, 5], [3, 6]]),
        ([[1], [2], [3]], [[1, 2, 3]]),
        ([[1, 2]], [[1], [2]]),
    ],
)
def test_transpose(matrix, expected):
    assert transpose(matrix) == expected


def test_transpose_returns_lists_not_tuples():
    assert all(isinstance(row, list) for row in transpose([[1, 2], [3, 4]]))


def test_transpose_twice_is_the_original():
    matrix = [[1, 2, 3], [4, 5, 6]]
    assert transpose(transpose(matrix)) == matrix


@pytest.mark.parametrize(
    "a, b, expected",
    [
        ([1, 2, 3], [2, 3, 4], [2, 3]),
        (["b", "a"], ["a", "c"], ["a"]),
        ([1, 1, 2], [2, 2], [2]),
        ([1], [2], []),
    ],
)
def test_common_items(a, b, expected):
    assert common_items(a, b) == expected
