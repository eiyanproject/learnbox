import functools
import math


@functools.total_ordering
class Vector:
    def __init__(self, items):
        self._items = tuple(float(x) for x in items)

    def __repr__(self):
        return f"Vector({list(self._items)})"

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __contains__(self, item):
        return item in self._items

    def __getitem__(self, index):
        if isinstance(index, slice):
            return Vector(self._items[index])
        return self._items[index]

    def _check(self, other):
        if not isinstance(other, Vector):
            return False
        if len(self) != len(other):
            raise ValueError("vectors must have the same length")
        return True

    def __add__(self, other):
        if not self._check(other):
            return NotImplemented
        return Vector(a + b for a, b in zip(self, other))

    def __sub__(self, other):
        if not self._check(other):
            return NotImplemented
        return Vector(a - b for a, b in zip(self, other))

    def __mul__(self, k):
        if not isinstance(k, (int, float)):
            return NotImplemented
        return Vector(a * k for a in self)

    __rmul__ = __mul__

    def __neg__(self):
        return self * -1

    def __abs__(self):
        return math.sqrt(sum(a * a for a in self))

    def __bool__(self):
        return any(self._items)

    def __eq__(self, other):
        return isinstance(other, Vector) and self._items == other._items

    def __hash__(self):
        return hash(self._items)

    def __lt__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return abs(self) < abs(other)
