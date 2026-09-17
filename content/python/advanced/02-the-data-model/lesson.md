---
title: The data model
summary: Make your own types behave like built-ins with dunder methods for length, indexing, iteration, arithmetic, hashing and ordering.
order: 2
files: [vector.py]
run: python -i vector.py
hints:
  - "Store the numbers as a tuple in `__init__`: `self._items = tuple(float(x) for x in items)`. `__len__`, `__iter__` and `__getitem__` then delegate to it."
  - "`__getitem__` with a slice should return a `Vector`: `if isinstance(index, slice): return Vector(self._items[index])`."
  - "`__add__`: return `NotImplemented` if `other` is not a `Vector`; raise `ValueError` on a length mismatch; otherwise `Vector(a + b for a, b in zip(self, other))`. `__mul__` with a number scales; define `__rmul__ = __mul__` for `3 * v`."
  - "`__eq__` compares tuples, `__hash__` is `hash(self._items)`, and `@functools.total_ordering` builds the other comparisons from `__eq__` and `__lt__` (compare by `abs()`)."
---

Python's syntax is a thin layer over special methods. `len(x)` calls
`x.__len__()`, `x[i]` calls `x.__getitem__(i)`, `a + b` calls `a.__add__(b)`.
Implement the right ones and your class works everywhere a built-in would.

## Representation

```python
def __repr__(self):  return f"Vector({list(self._items)})"   # for developers, repr() and the REPL
def __str__(self):   return "(1, 2)"                         # for users, str() and print(); falls back to __repr__
def __format__(self, spec): ...                              # f"{v:.2f}"
```

## Containers

```python
def __len__(self):             ...   # len(v); also makes empty objects falsy
def __getitem__(self, index):  ...   # v[0], v[-1], v[1:3]
def __iter__(self):            ...   # for x in v
def __contains__(self, item):  ...   # x in v  (falls back to __iter__)
```

`__getitem__` receives a `slice` object for `v[1:3]`. Return the same type for
slices, like lists and strings do.

## Arithmetic

```python
def __add__(self, other):
    if not isinstance(other, Vector):
        return NotImplemented          # not "raise": let Python try other.__radd__
    return Vector(a + b for a, b in zip(self, other))

def __mul__(self, k):  ...             # v * 3
def __rmul__(self, k): ...             # 3 * v: tried after int.__mul__ gives up
def __neg__(self):     ...             # -v
def __abs__(self):     ...             # abs(v)
```

Returning `NotImplemented` (a special value, not the exception) tells Python
"I do not know how to do this, ask the other operand". Only when both sides
return it does Python raise `TypeError`.

## Equality and hashing

```python
def __eq__(self, other):
    return isinstance(other, Vector) and self._items == other._items

def __hash__(self):
    return hash(self._items)
```

Defining `__eq__` sets `__hash__` to `None` unless you define it too, which makes
instances unhashable. Only make objects hashable if they are **immutable**:
a dict key whose hash changes is lost in the dict forever.

## Ordering

Define `__eq__` and `__lt__`, and `functools.total_ordering` fills in `<=`, `>`
and `>=`:

```python
@functools.total_ordering
class Version:
    def __eq__(self, other): ...
    def __lt__(self, other): ...
```

## Truthiness and calling

`__bool__` controls `if obj:` (without it, `__len__` is used). `__call__` makes
instances callable like functions.

## Your turn

In `vector.py`, write an immutable `Vector` of floats:

- `Vector([1, 2, 3])` stores floats; `repr` is `Vector([1.0, 2.0, 3.0])`
- `len`, iteration, `in`, indexing, and slicing (returning a `Vector`)
- `v + w` element-wise (lengths must match, else `ValueError`), `v - w`,
  `v * k` and `k * v` for numbers, `-v`
- `abs(v)` is the Euclidean length; `bool(v)` is false only for all-zeros
- `==` and `hash` by value; `<` etc. compare by `abs()`
- adding a non-`Vector` raises `TypeError` (via `NotImplemented`)
