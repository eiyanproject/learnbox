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

Why does `len()` work on lists, strings, dicts and files alike, and how can
`+` mean addition for numbers but joining for strings? Because Python's
syntax is a thin layer over **special methods** (the "dunder" methods, with
double underscores). `len(x)` calls `x.__len__()`, `x[i]` calls
`x.__getitem__(i)`, `a + b` calls `a.__add__(b)`. The full set of these
hooks, and the rules for how Python uses them, is called the **data model**.
Implement the right ones and your own class works everywhere a built-in
would: with `len`, `for`, `in`, `+`, `==`, `sorted`, as a dict key, and so
on.

You never call these methods by name. You define them, and Python calls
them when your object is used with the matching syntax.

## Representation

Two methods decide how an object turns into text. They are written here as
one-liners (a sketch of methods from a class, not runnable on its own):

```python
def __repr__(self):  return f"Vector({list(self._items)})"   # for developers, repr() and the REPL
def __str__(self):   return "(1, 2)"                         # for users, str() and print(); falls back to __repr__
def __format__(self, spec): ...                              # f"{v:.2f}"
```

- `__repr__` is the developer's view: what the `>>>` prompt shows, what
  `repr()` returns, and what you see in a list of objects or a debugging
  log. It should be unambiguous, ideally looking like the code that would
  recreate the object.
- `__str__` is the user's view: what `print()` and `str()` use. If you do not
  define it, Python uses `__repr__` instead, so defining only `__repr__` is
  common and fine.
- `__format__` receives the text after the colon in an f-string, such as
  `.2f`, so an object can support format specifications like a number does.

```pycon
>>> class Temp:
...     def __init__(self, c):
...         self.c = c
...     def __repr__(self):
...         return f"Temp({self.c})"
...     def __str__(self):
...         return f"{self.c} °C"
...
>>> t = Temp(21.5)
>>> t                 # the prompt uses __repr__
Temp(21.5)
>>> print(t)          # print uses __str__
21.5 °C
>>> [t]               # a list shows its items with __repr__
[Temp(21.5)]
```

## Containers

Four methods make an object act like a collection:

```python
def __len__(self):             ...   # len(v); also makes empty objects falsy
def __getitem__(self, index):  ...   # v[0], v[-1], v[1:3]
def __iter__(self):            ...   # for x in v
def __contains__(self, item):  ...   # x in v  (falls back to __iter__)
```

Most classes store their items in a built-in list or tuple and pass each
call on to it, which is called **delegating**:

```pycon
>>> class Playlist:
...     def __init__(self, songs):
...         self._songs = list(songs)
...     def __len__(self):
...         return len(self._songs)
...     def __getitem__(self, index):
...         return self._songs[index]
...     def __iter__(self):
...         return iter(self._songs)
...
>>> p = Playlist(["intro", "verse", "outro"])
>>> len(p), p[0], p[-1]
(3, 'intro', 'outro')
>>> "verse" in p          # no __contains__, so Python loops with __iter__
True
>>> [song.upper() for song in p]
['INTRO', 'VERSE', 'OUTRO']
>>> p[1:]                 # a slice of the list: a plain list, not a Playlist
['verse', 'outro']
```

`__iter__` must return an iterator (the Iterators lesson), and handing back
`iter()` of the stored list is the simplest way. `__contains__` is optional:
without it, `in` walks the items with `__iter__` until it finds a match.

`__getitem__` receives whatever was inside the square brackets. For `p[0]`
that is the integer `0`. For `p[1:3]` it is a **slice object**, `slice(1, 3,
None)`, which a list or tuple understands directly. As the last line shows,
passing it straight on returns a plain list. Lists return lists and strings
return strings when sliced, so a well-behaved container returns its own type
for slices too: check `isinstance(index, slice)` and wrap the result.

## Arithmetic

Operators map to methods as well: `+` is `__add__`, `-` is `__sub__`, `*`
is `__mul__`, unary minus (`-v`) is `__neg__`, and `abs(v)` is `__abs__`.
Each returns a new object; it should not change `self`.

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

The interesting part is what happens when the two sides are different
types. For `a + b`, Python:

1. calls `a.__add__(b)`;
2. if that returns the special value `NotImplemented`, calls the
   **reflected** method on the right-hand operand, `b.__radd__(a)`;
3. if that also returns `NotImplemented` (or does not exist), raises
   `TypeError`.

That is why `3 * v` needs `__rmul__`. `3 * v` first asks `int.__mul__(3, v)`,
and an `int` does not know what a `Vector` is, so it returns `NotImplemented`.
Python then tries `v.__rmul__(3)`, and your class gets its turn.

Returning `NotImplemented` (a special value, not the `NotImplementedError`
exception) tells Python "I do not know how to do this, ask the other
operand". Raising `TypeError` yourself would cut that conversation short and
stop the other type from ever handling the operation. Only when both sides
return it does Python raise `TypeError`, with a standard message:

```pycon
>>> class Meters:
...     def __init__(self, n):
...         self.n = n
...     def __add__(self, other):
...         if not isinstance(other, Meters):
...             return NotImplemented
...         return Meters(self.n + other.n)
...     def __rmul__(self, k):
...         return Meters(self.n * k)
...
>>> (Meters(2) + Meters(3)).n
5
>>> (3 * Meters(2)).n          # int gives up, then Meters.__rmul__ runs
6
>>> Meters(2) + 1
Traceback (most recent call last):
  ...
TypeError: unsupported operand type(s) for +: 'Meters' and 'int'
```

## Equality and hashing

```python
def __eq__(self, other):
    return isinstance(other, Vector) and self._items == other._items

def __hash__(self):
    return hash(self._items)
```

`__eq__` decides what `==` means. Without it, two objects are only equal if
they are the very same object. The `isinstance` check makes comparing with
an unrelated type give `False` rather than crash.

`__hash__` is what lets an object be a dict key or a set member. A dict files
each key under a number computed from it, its **hash**, and finds it again
later by computing the hash again. Two rules follow:

- Objects that are equal must have equal hashes, or the dict would look in
  the wrong place for one of them. Hashing the same tuple that `__eq__`
  compares guarantees this.
- The hash must never change while the object is in a dict or set.

Because of the first rule, defining `__eq__` sets `__hash__` to `None` unless
you define it too, which makes instances unhashable: Python cannot know that
its default hash still agrees with your new idea of equality. Because of the
second, only make objects hashable if they are **immutable**. A dict key
whose hash changes after it was stored is filed under the old number and can
never be found again; it is lost in the dict.

## Ordering

`<` calls `__lt__` ("less than"), `<=` calls `__le__`, `>` calls `__gt__` and
`>=` calls `__ge__`. Writing all four is repetitive, and they must agree with
each other. Define `__eq__` and `__lt__`, and the `functools.total_ordering`
class decorator fills in `<=`, `>` and `>=` from those two:

```pycon
>>> import functools
>>> @functools.total_ordering
... class Version:
...     def __init__(self, major, minor):
...         self.key = (major, minor)
...     def __eq__(self, other):
...         return self.key == other.key
...     def __lt__(self, other):
...         return self.key < other.key
...
>>> Version(1, 2) < Version(1, 10)
True
>>> Version(2, 0) >= Version(1, 9)      # filled in by total_ordering
True
```

`sorted()`, `min()` and `max()` only need `<`, so once `__lt__` exists those
work too.

## Truthiness and calling

`__bool__` controls what `if obj:` and `bool(obj)` decide. Without it,
Python uses `__len__`: an object of length 0 is false, anything else is
true. Without either, every object is true.

`__call__` makes instances callable like functions: `obj(5)` runs
`obj.__call__(5)`. It suits objects that are mostly one action but need to
remember settings.

```pycon
>>> class Multiplier:
...     def __init__(self, k):
...         self.k = k
...     def __call__(self, x):
...         return x * self.k
...
>>> triple = Multiplier(3)
>>> triple(5)
15
```

## Your turn

In `vector.py`, write an immutable `Vector` of floats. "Immutable" means
nothing can change a `Vector` after it is created, so every operation
returns a new one:

- `Vector([1, 2, 3])` stores the numbers as floats; its `repr` is
  `Vector([1.0, 2.0, 3.0])`.
- `len`, iteration, `in`, indexing (including negative indexes), and slicing,
  where a slice returns a `Vector`. Assigning to an item, `v[0] = 5`, must
  raise `TypeError` (storing the numbers in a tuple gives you that).
- `v + w` adds element by element (the lengths must match, else
  `ValueError`), `v - w` subtracts the same way, `v * k` and `k * v` multiply
  every element by a number, and `-v` negates every element.
- `abs(v)` is the Euclidean length, the square root of the sum of the
  squares: `abs(Vector([3, 4]))` is `5`. `bool(v)` is false only when every
  element is zero, and for the empty `Vector([])`.
- `==` and `hash` by value, so `Vector([1, 2]) == Vector([1.0, 2.0])` and two
  equal vectors count once in a set. A `Vector` never equals a tuple or list,
  even one with the same numbers.
- `<`, `<=`, `>` and `>=` compare by length, `abs()`, so `sorted()` orders
  vectors from shortest to longest.
- adding a non-`Vector`, such as `Vector([1]) + 1` or `Vector([1]) + [1]`,
  raises `TypeError`, by returning `NotImplemented` rather than raising it
  yourself.
