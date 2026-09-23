import pytest

from flow import append_safely, apply_all, describe_args, first_divisible


@pytest.mark.parametrize(
    "values, divisor, expected",
    [
        ([1, 3, 4, 6], 2, 4),
        ([5, 10, 15], 5, 5),
        ([1, 3, 5], 2, "none"),
        ([], 3, "none"),
    ],
)
def test_first_divisible(values, divisor, expected):
    assert first_divisible(values, divisor) == expected


def test_default_list_is_not_shared_between_calls():
    assert append_safely(1) == [1]
    assert append_safely(2) == [2]
    assert append_safely(3) == [3]


def test_append_safely_uses_the_list_it_is_given():
    target = [0]
    assert append_safely(1, target) == [0, 1]
    assert target == [0, 1]


def test_describe_args_counts_positional():
    result = describe_args(1, 2, 3)
    assert result["count"] == 3
    assert result["total"] == 6
    assert result["names"] == []


def test_describe_args_sorts_keyword_names():
    result = describe_args(b=1, a=2)
    assert result["names"] == ["a", "b"]
    assert result["count"] == 0
    assert result["total"] == 0


def test_describe_args_handles_both():
    result = describe_args(4, 5, zebra=1, apple=2)
    assert result == {"count": 2, "names": ["apple", "zebra"], "total": 9}


def test_apply_all_runs_in_order():
    assert apply_all([lambda x: x + 1, lambda x: x * 2], 3) == 8


def test_apply_all_order_matters():
    assert apply_all([lambda x: x * 2, lambda x: x + 1], 3) == 7


def test_apply_all_with_no_functions_returns_the_value():
    assert apply_all([], 42) == 42
