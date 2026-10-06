import pytest

from culprit import first_bad, minimal_failing


def counting(first):
    """An is_bad for which `first` is the first bad version, and a call log."""
    calls = []

    def is_bad(version):
        calls.append(version)
        return first is not None and version >= first

    return is_bad, calls


@pytest.mark.parametrize("first", [1, 2, 5, 6, 7, 8])
def test_finds_the_first_bad_version(first):
    is_bad, _ = counting(first)
    assert first_bad(8, is_bad) == first


def test_nothing_is_bad():
    is_bad, _ = counting(None)
    assert first_bad(8, is_bad) is None


def test_a_single_version():
    assert first_bad(1, counting(1)[0]) == 1
    assert first_bad(1, counting(None)[0]) is None


@pytest.mark.parametrize("n, first", [(800, 613), (800, 1), (800, 800), (1000000, 123457), (1000000, None), (7, 4)])
def test_it_halves_instead_of_walking(n, first):
    is_bad, calls = counting(first)
    assert first_bad(n, is_bad) == first
    assert len(calls) <= n.bit_length() + 1, f"{len(calls)} builds for {n} versions is too many"


def test_it_only_asks_about_real_versions():
    is_bad, calls = counting(3)
    first_bad(10, is_bad)
    assert all(1 <= v <= 10 for v in calls), f"asked about {calls}"


def both(a, b):
    return lambda items: a in items and b in items


def test_cuts_down_to_the_two_that_matter():
    assert minimal_failing([1, 3, 5, 7, 9], both(3, 7)) == [3, 7]


def test_keeps_the_original_order():
    assert minimal_failing(list("xbyaz"), both("a", "b")) == ["b", "a"]


def test_a_single_culprit():
    assert minimal_failing(list(range(60)), lambda items: 41 in items) == [41]


def test_already_minimal():
    assert minimal_failing([3, 7], both(3, 7)) == [3, 7]


def test_fails_whatever_is_left():
    assert minimal_failing([1, 2, 3], lambda items: True) == []


def test_a_failure_that_needs_a_count():
    # Fails while at least three items remain: any three will do, and the
    # procedure keeps the last three.
    assert minimal_failing([1, 2, 3, 4, 5], lambda items: len(items) >= 3) == [3, 4, 5]


def test_duplicates_are_separate_items():
    assert minimal_failing([7, 1, 7, 2, 7], lambda items: items.count(7) >= 2) == [7, 7]


def test_the_input_is_left_alone():
    items = [1, 3, 5, 7, 9]
    minimal_failing(items, both(3, 7))
    assert items == [1, 3, 5, 7, 9]


def test_the_result_really_is_minimal():
    fails = lambda items: sum(items) >= 10
    result = minimal_failing([4, 1, 6, 2, 5], fails)
    assert fails(result)
    for i in range(len(result)):
        assert not fails(result[:i] + result[i + 1:])
