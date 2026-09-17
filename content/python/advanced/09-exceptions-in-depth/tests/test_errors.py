import inspect

import pytest

import errors
from errors import AppError, count_by_kind, load_port, validate_all, with_row_note


def test_hierarchy():
    assert issubclass(errors.ConfigError, AppError)
    assert issubclass(errors.NetworkError, AppError)
    assert not issubclass(AppError, BaseException) or issubclass(AppError, Exception)
    e = errors.NetworkError("down", retryable=True)
    assert str(e) == "down" and e.retryable is True


def test_load_port_ok():
    assert load_port({"port": "8080"}) == 8080
    assert load_port({"port": 1}) == 1


def test_load_port_chains_cause():
    with pytest.raises(errors.ConfigError) as info:
        load_port({"port": "http"})
    assert isinstance(info.value.__cause__, ValueError)
    with pytest.raises(errors.ConfigError) as info:
        load_port({})
    assert isinstance(info.value.__cause__, KeyError)


def test_load_port_range_has_no_cause():
    with pytest.raises(errors.ConfigError) as info:
        load_port({"port": "70000"})
    assert info.value.__cause__ is None
    assert info.value.__suppress_context__ is True


def test_with_row_note():
    def check(row):
        if row < 0:
            raise ValueError("negative")

    with_row_note(check, [1, 2])
    with pytest.raises(ValueError) as info:
        with_row_note(check, [5, 6, -1])
    assert info.value.__notes__ == ["row 2"]
    assert str(info.value) == "negative"


def test_validate_all_ok():
    assert validate_all([{"id": 1, "qty": 0}, {"id": 2, "qty": 5}]) is True


def test_validate_all_groups_every_problem():
    records = [{"qty": 1}, {"id": 2, "qty": -1}, {"qty": -5}]
    with pytest.raises(ExceptionGroup) as info:
        validate_all(records)
    kinds = sorted(type(e).__name__ for e in info.value.exceptions)
    assert kinds == ["KeyError", "KeyError", "ValueError", "ValueError"]


def test_count_by_kind():
    assert count_by_kind([{"qty": 1}, {"id": 2, "qty": -1}, {"qty": -5}]) == {"key": 2, "value": 2}
    assert count_by_kind([{"id": 1, "qty": 1}]) == {"key": 0, "value": 0}


def test_count_by_kind_uses_except_star():
    assert "except*" in inspect.getsource(count_by_kind)
