import os
import time

import pytest

from contexts import Timer, Transaction, changed_dir, ignore_errors


def test_timer_measures():
    with Timer() as t:
        time.sleep(0.05)
    assert 0.04 < t.elapsed < 1


def test_timer_does_not_swallow_exceptions():
    t = Timer()
    with pytest.raises(KeyError):
        with t:
            raise KeyError("boom")
    assert t.elapsed >= 0


def test_changed_dir(tmp_path):
    before = os.getcwd()
    with changed_dir(tmp_path):
        assert os.path.samefile(os.getcwd(), tmp_path)
    assert os.getcwd() == before


def test_changed_dir_restores_after_error(tmp_path):
    before = os.getcwd()
    with pytest.raises(RuntimeError):
        with changed_dir(tmp_path):
            raise RuntimeError
    assert os.getcwd() == before


def test_ignore_errors_suppresses_listed():
    with ignore_errors(KeyError, ZeroDivisionError):
        1 / 0
    with ignore_errors(KeyError):
        {}["x"]


def test_ignore_errors_lets_others_through():
    with pytest.raises(ValueError):
        with ignore_errors(KeyError):
            raise ValueError


def test_transaction_commits():
    d = {"balance": 10}
    with Transaction(d) as working:
        working["balance"] -= 3
        working["note"] = "paid"
        assert d == {"balance": 10}, "changes must not show until the block ends"
    assert d == {"balance": 7, "note": "paid"}


def test_transaction_rolls_back():
    d = {"balance": 10}
    with pytest.raises(ValueError):
        with Transaction(d) as working:
            working["balance"] = -5
            raise ValueError("insufficient funds")
    assert d == {"balance": 10}


def test_transaction_commit_removes_deleted_keys():
    d = {"a": 1, "b": 2}
    with Transaction(d) as working:
        del working["b"]
    assert d == {"a": 1}
