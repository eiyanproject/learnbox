import dataclasses

import pytest

from models import Money, Priority, Task


def test_priority_enum():
    assert [p.name for p in Priority] == ["LOW", "MEDIUM", "HIGH"]
    assert Priority(3) is Priority.HIGH
    assert Priority.LOW.value == 1


def test_task_is_a_dataclass_with_defaults():
    assert dataclasses.is_dataclass(Task)
    t = Task("write tests")
    assert t.priority is Priority.MEDIUM
    assert t.tags == []
    assert t.done is False


def test_task_tags_not_shared():
    a, b = Task("a"), Task("b")
    a.tags.append("x")
    assert b.tags == []


def test_task_repr_hides_sort_key():
    r = repr(Task("x", Priority.HIGH))
    assert "sort_key" not in r
    assert "title='x'" in r


def test_sort_key_is_not_an_init_argument():
    with pytest.raises(TypeError):
        Task(sort_key=(0, ""), title="x")


def test_tasks_sort_by_priority_then_title():
    tasks = [
        Task("b-low", Priority.LOW),
        Task("z-high", Priority.HIGH),
        Task("a-high", Priority.HIGH, tags=["urgent"]),
        Task("m-medium"),
    ]
    assert [t.title for t in sorted(tasks)] == ["a-high", "z-high", "m-medium", "b-low"]


def test_money_is_frozen_and_hashable():
    m = Money(500, "IDR")
    with pytest.raises(dataclasses.FrozenInstanceError):
        m.amount = 1
    assert {m, Money(500, "IDR")} == {m}


def test_money_rejects_negative():
    with pytest.raises(ValueError):
        Money(-1, "USD")


def test_money_addition():
    assert Money(150, "USD") + Money(250, "USD") == Money(400, "USD")
    with pytest.raises(ValueError):
        Money(1, "USD") + Money(1, "EUR")
