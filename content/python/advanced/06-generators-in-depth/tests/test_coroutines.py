import inspect
import pathlib

import pytest

from coroutines import accumulate_until_none, batch_totals, primed, running_average


def test_primed_advances_to_first_yield():
    @primed
    def gen():
        x = yield "ready"
        yield f"got {x}"

    g = gen()
    assert inspect.getgeneratorstate(g) == inspect.GEN_SUSPENDED
    assert g.send("a") == "got a"


def test_primed_keeps_name():
    @primed
    def my_gen():
        yield

    assert my_gen.__name__ == "my_gen"


def test_running_average():
    avg = running_average()
    assert avg.send(10) == 10
    assert avg.send(20) == 15
    assert avg.send(0) == 10


def test_running_averages_are_independent():
    a, b = running_average(), running_average()
    a.send(100)
    assert b.send(1) == 1


def test_accumulate_returns_total():
    g = accumulate_until_none()
    next(g)
    g.send(5)
    g.send(7)
    with pytest.raises(StopIteration) as stop:
        g.send(None)
    assert stop.value.value == 12


def test_batch_totals():
    results = []
    b = batch_totals(results)
    for x in (1, 2, 3):
        b.send(x)
    b.send(None)
    b.send(10)
    b.send(None)
    b.send(None)
    assert results == [6, 10, 0]


def test_batch_totals_uses_yield_from():
    source = inspect.getsource(batch_totals.__wrapped__)
    assert "yield from" in source


def test_generator_close_is_clean():
    avg = running_average()
    avg.send(1)
    avg.close()
    assert inspect.getgeneratorstate(avg) == inspect.GEN_CLOSED
    assert pathlib.Path(__file__).exists()
