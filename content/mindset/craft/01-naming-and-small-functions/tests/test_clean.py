import inspect

import pytest

from clean import categorise, is_expired, is_expiring_soon


def test_expired_is_negative_days():
    assert is_expired(-1)
    assert not is_expired(0)
    assert not is_expired(5)


def test_expiring_soon_is_inside_the_window():
    assert is_expiring_soon(2, 7)
    assert not is_expiring_soon(10, 7)


def test_expiring_soon_excludes_already_expired():
    assert not is_expiring_soon(-1, 7), "something expired is not 'expiring soon'"


def test_the_boundary_of_the_window():
    assert is_expiring_soon(6, 7)
    assert not is_expiring_soon(7, 7), "the window is strictly less than warning_days"


@pytest.mark.parametrize(
    "days, window, expected",
    [(-5, 7, "expired"), (-1, 7, "expired"), (0, 7, "expiring soon"),
     (3, 7, "expiring soon"), (7, 7, "fresh"), (30, 7, "fresh")],
)
def test_categorise(days, window, expected):
    assert categorise(days, window) == expected


def test_parameters_are_named_meaningfully():
    names = list(inspect.signature(categorise).parameters)
    assert names == ["days_until_expiry", "warning_days"], (
        f"the parameter names are the documentation; got {names}"
    )


def test_categorise_reads_as_a_summary():
    """It should delegate, not recompute: no bare comparisons of its own."""
    source = inspect.getsource(categorise)
    assert "is_expired" in source and "is_expiring_soon" in source, (
        "categorise should use the predicates rather than repeating their logic"
    )


def test_predicates_return_booleans():
    assert is_expired(-1) is True
    assert is_expired(1) is False
