---
title: Functional tools
summary: partial, reduce, singledispatch, cached_property and the operator module.
order: 5
files: [functional.py]
run: python -i functional.py
hints:
  - "`compose(*funcs)`: `return functools.reduce(lambda f, g: lambda x: g(f(x)), funcs, lambda x: x)` applies them left to right."
  - "`to_json_like` is `@functools.singledispatch` with a default that raises `TypeError`, plus `@to_json_like.register` functions for `dict`, `list`, `str`, `int`/`float` (register both), and `bool` (it must come out as `\"true\"`/`\"false\"`)."
  - "`by_fields(*names)`: `operator.attrgetter(*names)` is a ready-made key function."
  - "`Report.summary` is a `@functools.cached_property`; count calls in `self.computations` to prove it runs once."
---

## functools.partial

Pre-fill some arguments of a function to make a new one:

```python
from functools import partial

int_from_binary = partial(int, base=2)
int_from_binary("1010")          # 10

log_error = partial(log, level="ERROR")
```

Unlike a `lambda`, a `partial` keeps a readable repr and can be pickled.

## functools.reduce

Fold a sequence into one value by repeatedly combining:

```python
from functools import reduce
reduce(lambda acc, x: acc * x, [1, 2, 3, 4], 1)     # 24
```

Most folds have a clearer built-in (`sum`, `max`, `"".join`, `any`). `reduce`
earns its place for things like composing functions or merging dicts.

## The operator module

Function versions of operators and lookups, faster and clearer than lambdas:

```python
import operator as op

reduce(op.mul, nums, 1)
sorted(users, key=op.attrgetter("last", "first"))
sorted(rows, key=op.itemgetter(2))
list(map(op.methodcaller("strip"), lines))
```

## singledispatch

One function name, different implementations chosen by the **type of the first
argument**. It is the functional alternative to a long `if isinstance` chain,
and it is open to extension: other modules can register new types.

```python
from functools import singledispatch

@singledispatch
def describe(x):
    raise TypeError(f"cannot describe {type(x).__name__}")

@describe.register
def _(x: int):
    return f"the number {x}"

@describe.register
def _(x: list):
    return f"a list of {len(x)}"
```

Dispatch follows the class hierarchy, choosing the most specific registration.
Watch out: `bool` is a subclass of `int`, so `True` goes to the `int` version
unless you register `bool` too. `None` is not a class, so register its type
explicitly: `@describe.register(type(None))`. `singledispatchmethod` does the
same for methods.

## cached_property

A property computed on first access, then stored on the instance:

```python
from functools import cached_property

class Dataset:
    @cached_property
    def stats(self):
        return expensive_analysis(self.rows)
```

`del obj.stats` clears the cache. It needs an instance `__dict__`, so it does
not work with `__slots__`.

## Your turn

In `functional.py`:

- `compose(*funcs)`: one function applying `funcs` **left to right**;
  `compose()` is the identity
- `parse_bits`: a `functools.partial` of `int` that parses binary strings
- `to_json_like(value)`: a `singledispatch` function producing JSON text for
  `dict` (keys sorted, `{"a": 1}` style), `list`, `str` (double-quoted),
  `int`, `float`, `bool` (`true`/`false`) and `None` (`null`); other types raise
  `TypeError`. Nested values must work.
- `by_fields(*names)`: a key function sorting objects by those attributes, using `operator`
- `Report(rows)`: `summary` is a `cached_property` returning
  `{"count": ..., "total": ...}` of `rows`; `self.computations` counts how many
  times it was actually computed
