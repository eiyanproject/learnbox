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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **functional style** | building programs by passing functions around as values |
| **glue code** | small code connecting other pieces, such as one-line lambdas |
| **partial application** | making a new function with some arguments already filled in |
| **binary** (base 2) | numbers written with only 0 and 1: `"1010"` is 10 |
| **pickle** | save a Python object as bytes, or send it to another process; a `partial` can be pickled, a lambda cannot |
| **fold** (reduce) | combining a sequence into one value, carrying a running result |
| **accumulator** | that running result (`acc`) |
| **dict merge** (`a \| b`) | a new dict with both; the right side wins on duplicate keys |
| **generic function** | one name with different implementations chosen by the type of the first argument |
| **dispatch** | choosing the implementation; it follows the class hierarchy, most specific first |
| **fallback** | the implementation used when no registered type matches |
| **subclass** | `bool` is a subclass of `int`, so it needs its own registration |
| **cached property** | computed on first access, then stored on the instance |
| **compose** | combine functions so each gets the previous one's result |
| **JSON** | text data: `{"a": 1}`, `[1, 2]`, `"text"`, `true`, `false`, `null` |
| **key function** | a function `sorted` calls on each item to decide its order |

### Python functions

| Name | What it does |
|---|---|
| `functools.partial(func, *args, **kwargs)` | `func` with those arguments filled in |
| `int(text, base=2)` | reads the text as a binary number |
| `functools.reduce(func, items, start)` | folds the items into one value, starting from `start` |
| `import operator as op` | function versions of operators |
| `op.mul`, `op.add` | `a * b`; `a + b` |
| `op.itemgetter(2)` | a function returning `x[2]` |
| `op.attrgetter("last", "first")` | a function returning those attributes as a tuple |
| `op.methodcaller("strip")` | a function calling `.strip()` on its argument |
| `types.SimpleNamespace(a=1)` | a quick object with the attributes you name |
| `@functools.singledispatch` | makes a generic function |
| `@f.register`, `@f.register(int)` | adds an implementation, by the first parameter's annotation or a named type |
| `type(None)` | the type of `None`, for registering it |
| `functools.singledispatchmethod` | the same for methods, dispatching on the argument after `self` |
| `@functools.cached_property` | computes once, then stores the value |
| `del obj.prop` | clears a cached property |
| `json.loads(text)` | reads JSON text back, as the test does |
| `str.strip`, `str.upper` | methods taken from the class, usable as plain functions |

### Errors

| Error | Means |
|---|---|
| `TypeError` | the fallback for a type with no implementation, such as a set |

---

Since the Intermediate section you have been passing functions around as
values: as `key=` for sorting, into decorators, out of closures. The
`functools` and `operator` modules are toolboxes for exactly that style.
They give you ready-made ways to build new functions from old ones, to pick
an implementation by the type of a value, and to cache an expensive result,
so you write less glue code and the glue you do write is clearer.

## functools.partial

`partial(func, *args, **kwargs)` makes a new function that is `func` with
some of its arguments already filled in. Calling the new function supplies
the rest:

```pycon
>>> from functools import partial
>>> int_from_binary = partial(int, base=2)
>>> int_from_binary("1010")
10
>>> int_from_binary          # it shows what it wraps
functools.partial(<class 'int'>, base=2)
```

`int(text, base=2)` reads `text` as a number in base 2 (binary), so
`int_from_binary("1010")` means `int("1010", base=2)`, which is 10. The
`partial` remembered `base=2`; the call supplied `"1010"`.

The same move turns a general function into a specific one without writing
a new `def`. A general `log(message, level)` becomes
`log_error = partial(log, level="ERROR")`, and `log_error("disk full")` is
`log("disk full", level="ERROR")`:

```pycon
>>> def log(message, level):
...     return f"[{level}] {message}"
...
>>> log_error = partial(log, level="ERROR")
>>> log_error("disk full")
'[ERROR] disk full'
```

A `lambda` could do the same (`lambda m: log(m, level="ERROR")`), but a
`partial` keeps a readable `repr`, as above, which helps when debugging, and
it can be **pickled**: saved with the `pickle` module or sent to another
process, which a lambda cannot. That matters for the process pools in the
Pro section.

## functools.reduce

`reduce(func, items, start)` **folds** a sequence into one value. It starts
with `start`, combines it with the first item using `func`, combines that
result with the second item, and so on, carrying a running result (the
**accumulator**, `acc` below) along:

```pycon
>>> from functools import reduce
>>> reduce(lambda acc, x: acc * x, [1, 2, 3, 4], 1)     # (((1*1)*2)*3)*4
24
```

Step by step: `acc` starts at 1. With 1 it becomes 1, with 2 it becomes 2,
with 3 it becomes 6, and with 4 it becomes 24. It is the accumulator loop
from the Beginner section, written as one call. Leaving out `start` uses the
first item instead, which fails on an empty list, so passing it is safer.

Most folds have a clearer built-in (`sum`, `max`, `"".join`, `any`), and
those should win when they fit. `reduce` earns its place for combinations
that have no built-in, like composing functions or merging a list of dicts:

```pycon
>>> reduce(lambda a, b: a | b, [{"x": 1}, {"y": 2}, {"x": 3}], {})
{'x': 3, 'y': 2}
```

(`a | b` merges two dicts into a new one, and the right-hand side wins on
duplicate keys, so the later `"x": 3` replaces `"x": 1`.)

## The operator module

`operator` provides function versions of Python's operators and lookups:
`op.mul(a, b)` is `a * b`, `op.add(a, b)` is `a + b`. They are handy wherever
a function is expected, faster than the equivalent lambdas, and say what
they do by name:

```pycon
>>> import operator as op
>>> reduce(op.mul, [1, 2, 3, 4], 1)
24
>>> rows = [("ana", "red", 31), ("budi", "blue", 27)]
>>> sorted(rows, key=op.itemgetter(2))       # by the third field
[('budi', 'blue', 27), ('ana', 'red', 31)]
>>> list(map(op.methodcaller("strip"), ["  a ", "b  "]))
['a', 'b']
```

- `op.itemgetter(2)` makes a function that returns `x[2]` for whatever `x`
  it is given, the same as `lambda row: row[2]`.
- `op.methodcaller("strip")` makes a function that calls `.strip()` on its
  argument, the same as `lambda s: s.strip()`.

`op.attrgetter("last", "first")` does for attributes what `itemgetter` does
for positions. Given several names, it returns a tuple of them, so it sorts
by the first attribute and breaks ties with the second:

```pycon
>>> from types import SimpleNamespace
>>> users = [SimpleNamespace(last="Lim", first="Bo"), SimpleNamespace(last="Ali", first="Cy")]
>>> get = op.attrgetter("last", "first")
>>> get(users[0])
('Lim', 'Bo')
>>> [u.last for u in sorted(users, key=get)]
['Ali', 'Lim']
```

(`SimpleNamespace` is a quick object whose attributes you set by keyword;
it is handy for examples and tests.)

## singledispatch

Sometimes one operation needs a different implementation for each type of
value: describing, serialising or printing an int, a list or a dict. The
usual first attempt is a long `if isinstance(x, int): ... elif isinstance(x,
list): ...` chain, which has to be edited every time a new type appears.

`@singledispatch` turns a function into a **generic function**: one function
name, different implementations chosen by the **type of the first
argument**. The decorated function is the fallback for types nothing else
handles, and `.register` adds an implementation for a type. It is open to
extension: other modules can register new types without touching the
original code.

```pycon
>>> from functools import singledispatch
>>> @singledispatch
... def describe(x):
...     raise TypeError(f"cannot describe {type(x).__name__}")
...
>>> @describe.register
... def _(x: int):
...     return f"the number {x}"
...
>>> @describe.register
... def _(x: list):
...     return f"a list of {len(x)}"
...
>>> describe(7)
'the number 7'
>>> describe([1, 2])
'a list of 2'
>>> describe(True)           # see below
'the number True'
>>> describe("hi")
Traceback (most recent call last):
  ...
TypeError: cannot describe str
```

How it reads:

- `register` looks at the **type annotation** on the first parameter
  (`x: int`) to see which type an implementation is for. You can also name
  the type directly: `@describe.register(int)`.
- The implementations are named `_` by convention, because you never call
  them by name; you always call `describe`, and it picks one.
- `describe("hi")` has no `str` registration, so the original function runs,
  which here raises `TypeError`.

Dispatch follows the class hierarchy, choosing the most specific
registration. Watch out: `bool` is a subclass of `int`, so `True` goes to the
`int` version unless you register `bool` too; once you do, the `bool`
version wins for `True` and `False`, being more specific. `None` is not a
class, so register its type explicitly: `@describe.register(type(None))`.
`singledispatchmethod` does the same for methods in a class, dispatching on
the first argument after `self`.

An implementation can call the generic function again on the parts of a
value, which is how a nested structure is handled: the `list` version can
call `describe` on each item, and each item is dispatched by its own type.

## cached_property

Some attributes are expensive to compute but never change once the object
exists: a summary of a large dataset, a parsed file. A `@cached_property` is
a property computed on first access, then stored on the instance, so every
later read is a plain attribute lookup:

```pycon
>>> from functools import cached_property
>>> class Dataset:
...     def __init__(self, rows):
...         self.rows = rows
...     @cached_property
...     def stats(self):
...         print("computing...")
...         return {"n": len(self.rows), "sum": sum(self.rows)}
...
>>> d = Dataset([3, 4, 5])
>>> d.stats
computing...
{'n': 3, 'sum': 12}
>>> d.stats                 # second read: cached, nothing printed
{'n': 3, 'sum': 12}
>>> del d.stats             # clear the cache...
>>> d.stats                 # ...so it is computed again
computing...
{'n': 3, 'sum': 12}
```

`del obj.stats` clears the cache, for when the data underneath has changed.
The cached value is stored in the instance's `__dict__` under the property's
name, so it needs an instance `__dict__`, and it does not work with
`__slots__`.

## Your turn

In `functional.py`:

- `compose(*funcs)`: returns one function that applies `funcs` **left to
  right**: the first function gets the argument, the next gets its result.
  `compose(str.strip, str.upper)("  hi ")` is `"HI"`. `compose()` with no
  functions returns its argument unchanged.
- `parse_bits`: a `functools.partial` of `int` (a test checks the type) that
  parses binary strings: `parse_bits("101")` is `5`.
- `to_json_like(value)`: a `singledispatch` function that returns the JSON
  text for a value. One implementation per type:

  | Type | Output |
  |---|---|
  | `dict` | `{"a": 1, "b": 2}`, keys sorted, `", "` between pairs, `": "` after a key |
  | `list` | `[1, 2]`, `", "` between items |
  | `str` | the text in double quotes |
  | `int`, `float` | the number |
  | `bool` | `true` or `false` |
  | `None` | `null` |

  Any other type, such as a set, raises `TypeError`. Values inside a dict or a
  list are converted the same way, however deep, by calling `to_json_like`
  on them: `to_json_like({"b": [1, 2.5, None], "a": True})` is
  `'{"a": true, "b": [1, 2.5, null]}'`. Remember that `bool` is a subclass of
  `int`, so it needs its own registration. The result must be valid JSON
  (a test reads it back with `json.loads`).
- `by_fields(*names)`: returns a key function for `sorted` that orders
  objects by those attributes, first name first, built with the `operator`
  module.
- `Report(rows)`: `summary` is a `cached_property` returning
  `{"count": ..., "total": ...}`, the number of rows and their sum.
  `self.computations` starts at `0` and counts how many times the summary was
  actually worked out, which should stay at `1` however often it is read
  (and go up again only after `del report.summary`).
