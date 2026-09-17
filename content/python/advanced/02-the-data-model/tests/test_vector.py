import math

import pytest

from vector import Vector


def test_repr_and_floats():
    assert repr(Vector([1, 2, 3])) == "Vector([1.0, 2.0, 3.0])"


def test_container_protocol():
    v = Vector([3, 4, 5])
    assert len(v) == 3
    assert list(v) == [3.0, 4.0, 5.0]
    assert 4 in v and 9 not in v
    assert v[0] == 3.0 and v[-1] == 5.0


def test_slicing_returns_vector():
    v = Vector([1, 2, 3, 4])
    s = v[1:3]
    assert isinstance(s, Vector)
    assert s == Vector([2, 3])


def test_add_sub():
    assert Vector([1, 2]) + Vector([10, 20]) == Vector([11, 22])
    assert Vector([5, 5]) - Vector([1, 2]) == Vector([4, 3])


def test_length_mismatch():
    with pytest.raises(ValueError):
        Vector([1]) + Vector([1, 2])


def test_add_wrong_type_is_type_error():
    with pytest.raises(TypeError):
        Vector([1]) + 1
    with pytest.raises(TypeError):
        Vector([1]) + [1]


def test_scalar_multiplication_both_sides():
    assert Vector([1, 2]) * 3 == Vector([3, 6])
    assert 3 * Vector([1, 2]) == Vector([3, 6])
    assert -Vector([1, -2]) == Vector([-1, 2])


def test_abs_and_bool():
    assert abs(Vector([3, 4])) == 5
    assert bool(Vector([0, 0])) is False
    assert bool(Vector([0, 0.1])) is True
    assert bool(Vector([])) is False


def test_hash_and_equality():
    assert Vector([1, 2]) == Vector([1.0, 2.0])
    assert Vector([1, 2]) != (1.0, 2.0)
    assert len({Vector([1, 2]), Vector([1, 2]), Vector([2, 1])}) == 2


def test_ordering_by_magnitude():
    small, big = Vector([1, 1]), Vector([3, 4])
    assert small < big and big > small
    assert small <= Vector([1, 1]) and big >= small
    assert sorted([big, small]) == [small, big]


def test_immutable_storage():
    v = Vector([1, 2])
    with pytest.raises(TypeError):
        v[0] = 5
    assert math.isclose(abs(v), math.sqrt(5))
