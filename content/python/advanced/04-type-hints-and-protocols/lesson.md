---
title: Type hints and protocols
summary: Annotate code for readers and checkers, write generic functions and classes, and describe interfaces structurally with Protocol.
order: 4
files: [typed.py]
run: python -i typed.py
hints:
  - "`first(items: Sequence[T]) -> T | None`: `return items[0] if items else None`, with `T = TypeVar(\"T\")`."
  - "`Stack(Generic[T])` wraps a `list[T]`; `pop` raises `IndexError` when empty. Annotate every method."
  - "`SupportsArea(Protocol)` declares `def area(self) -> float: ...`; decorate it with `@runtime_checkable` so `isinstance` works."
  - "`parse_config` returns a `Config` `TypedDict` (`host: str`, `port: int`, `debug: bool`). Convert the port with `int(...)` and debug with `value.lower() in (\"1\", \"true\", \"yes\")`."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **type hint** (annotation) | a note in the code of what type a value should have; Python ignores it at runtime |
| **type checker** | a tool such as `mypy` or `pyright` that reads the program and reports type mistakes before it runs |
| **runtime** | while the program is actually running |
| **autocompletion** | an editor suggesting names as you type, using hints |
| **return annotation** (`-> str`) | the type of the return value; `-> None` returns nothing |
| **`int \| None`** | "an `int`, or `None`"; for anything that may be missing |
| **type alias** | a name for a type: `Mode = Literal["r", "w", "a"]` |
| **generic** | working on any type while linking the types together |
| **type variable** (`TypeVar`) | a placeholder type: "whatever goes in, the same comes out" |
| **generic class** | a class parameterised by a type: `Box[int]`, via `Generic[T]` |
| **specialised type** | a generic class with its type filled in: `Box[str]` |
| **Protocol** | an interface judged only by the methods an object has, whatever it inherits from |
| **structural typing** | judging a type by its structure (its methods), not its ancestry |
| **duck typing** | "if it walks like a duck and quacks like a duck, it is a duck" |
| **nominal typing** | judging by inheritance, as abstract base classes do |
| **`TypedDict`** | a dict with a fixed set of keys, each with its own type; a plain `dict` at runtime |
| **stack** | a collection where the last item pushed is the first popped |
| **push** / **pop** / **peek** | add on top / remove and return the top / look at the top without removing |

### Python names

| Name | What it does |
|---|---|
| `name: str`, `times: int = 1` | annotate a parameter, with or without a default |
| `list[str]`, `dict[str, float]` | a list of strings; a dict from strings to floats |
| `f.__annotations__` | the stored annotations of a function |
| `typing.get_type_hints(f)` | the annotations, with string annotations resolved |
| `Iterable[float]` | anything you can loop over that gives floats |
| `Sequence[T]` | something with a length and indexing |
| `Mapping` | any read-only dict-like type |
| `Callable[[int], str]` | a function taking one `int` and returning a `str` |
| `Literal["r", "w"]` | only those exact values |
| `Any` | anything; the checker stops checking |
| `T = TypeVar("T")` | creates a type variable |
| `class Box(Generic[T]):` | a generic class |
| `def last[T](items: Sequence[T]) -> T`, `class Box[T]:` | the shorter Python 3.12 syntax |
| `class Closeable(Protocol):` | declares a protocol |
| `@runtime_checkable` | lets `isinstance` check a protocol (methods exist, nothing more) |
| `class User(TypedDict):` | declares the keys and types of a dict |
| `value.lower() in ("1", "true", "yes")` | a case-insensitive check against several values |
| `raw.get("debug", "")` | a value, or a default when the key is missing |

### Errors

| Error | Means |
|---|---|
| `IndexError` | popping an empty stack |

---

Reading `def send(message, retries):`, you cannot tell whether `message` is
a string, a dict or an object, or whether `retries` is a count or a flag. You
have to read the body, or the documentation, or guess. **Type hints** write
that information into the code itself: what a function expects and what it
returns.

Python ignores them at runtime: a wrong type is not an error when the code
runs. Tools use them instead. Editors use them for autocompletion and inline
warnings, and **type checkers** such as `mypy` or `pyright` read your whole
program and report type mistakes, such as passing a `str` where an `int` is
needed, before the code ever runs. On a large codebase, that catches a whole
category of bugs for free.

```python
def greet(name: str, times: int = 1) -> str:
    return f"hi {name} " * times

count: int = 0
names: list[str] = []
scores: dict[str, float] = {}
maybe: int | None = None
```

Reading the syntax:

- `name: str` after a parameter means "this should be a `str`". A default
  comes after the type: `times: int = 1`.
- `-> str` before the colon is the type of the return value. A function that
  returns nothing is `-> None`.
- `count: int = 0` annotates a variable.
- Square brackets say what a collection holds: `list[str]` is a list of
  strings, and `dict[str, float]` a dict from strings to floats.
- `int | None` means "an `int`, or `None`". Use it for anything that may be
  missing.

And Python really does not check them:

```pycon
>>> def greet(name: str, times: int = 1) -> str:
...     return f"hi {name} " * times
...
>>> greet("ana", 2)
'hi ana hi ana '
>>> greet(42)           # wrong type, but Python runs it anyway
'hi 42 '
```

A type checker would flag `greet(42)`; Python itself only stores the
annotations on the function, where tools (and tests) can read them:

```pycon
>>> greet.__annotations__
{'name': <class 'str'>, 'times': <class 'int'>, 'return': <class 'str'>}
>>> import typing
>>> typing.get_type_hints(greet)["times"]
<class 'int'>
```

`typing.get_type_hints` is the more reliable of the two, because it also
resolves annotations written as strings.

## The useful vocabulary

The `typing` module (and `collections.abc`) provides names for the kinds of
things functions commonly take:

```python
from typing import Any, Callable, Iterable, Iterator, Literal, Sequence, TypeVar

def total(xs: Iterable[float]) -> float: ...            # accept any iterable, not only list
def apply(f: Callable[[int], str], x: int) -> str: ...
Mode = Literal["r", "w", "a"]                            # only these values
def open_file(path: str, mode: Mode = "r") -> None: ...
```

(Signatures only: the `...` bodies stand for real code.)

- `Iterable[float]`: anything you can loop over that gives floats: a list, a
  tuple, a set, a generator.
- `Sequence[T]`: something with a length and indexing, such as a list, tuple
  or string.
- `Callable[[int], str]`: a function that takes one `int` and returns a
  `str`. The first part, in its own brackets, lists the argument types.
- `Literal["r", "w", "a"]`: only these exact values are allowed.
- `Any`: anything at all; the checker stops checking. Use it sparingly.
- `Mode = Literal[...]` gives a type a name, a **type alias**, so it can be
  reused and read easily.

Accept the most general type you can (`Iterable`, `Sequence`, `Mapping`) and
return the most specific one (`list[str]`). A function that only loops over
its argument should say `Iterable`, so callers can pass a tuple or a
generator, not only a list. A function that returns a list should say
`list[str]`, so callers know they can index it, append to it and so on.

## Generics

Some functions work on any type, but connect their types together. `last`
returns an item of whatever sequence it was given. Writing `-> Any` would
throw that information away. A `TypeVar` (type variable) is a placeholder
that links types together: "whatever type goes in, that same type comes
out":

```python
T = TypeVar("T")

def last(items: Sequence[T]) -> T:
    return items[-1]

last([1, 2, 3])      # a checker knows this is int
last("abc")          # and this is str
```

Each call fills in `T` from its argument. With a `list[int]`, `T` is `int`,
so the checker knows the result is an `int` and can flag `last([1, 2]) + "x"`
as a mistake.

Classes can be generic too, by inheriting from `Generic[T]`. A `Box[int]` is
then a box of ints, and its methods' `T` means `int`:

```python
from typing import Generic

class Box(Generic[T]):
    def __init__(self, item: T) -> None:
        self.item = item

    def get(self) -> T:
        return self.item
```

```pycon
>>> from typing import Generic, TypeVar
>>> T = TypeVar("T")
>>> class Box(Generic[T]):
...     def __init__(self, item: T) -> None:
...         self.item = item
...     def get(self) -> T:
...         return self.item
...
>>> b: Box[int] = Box(5)
>>> b.get()
5
>>> Box[str]          # subscripting the class names a specialised type
__main__.Box[str]
```

(Python 3.12 adds the shorter `def last[T](items: Sequence[T]) -> T` and
`class Box[T]:` syntax, which creates the type variable for you.)

## Protocol: structural typing

An abstract base class (from the first lesson of this section) requires
subclasses to inherit from it: a class is a `Storage` only if it says
`class X(Storage)`. A **Protocol** only requires the right methods, whatever
the class inherits from. This is called **structural typing**: a type is
judged by its structure, the methods it has, not by its ancestry. That
matches how Python code is actually written, often called **duck typing**
("if it walks like a duck and quacks like a duck, it is a duck"):

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...

def shutdown(things: list[Closeable]) -> None:
    for t in things:
        t.close()
```

`Closeable` says "anything with a `close()` method that returns nothing".
Files, sockets and your own classes all satisfy `Closeable` without knowing
it exists. That is the big advantage over an ABC: you can describe an
interface for classes you did not write and cannot change.

A protocol is mostly for type checkers. `@runtime_checkable` also allows
`isinstance(x, Closeable)` at runtime, which checks only that the methods
exist, not their arguments or return types:

```pycon
>>> from typing import Protocol, runtime_checkable
>>> @runtime_checkable
... class Closeable(Protocol):
...     def close(self) -> None: ...
...
>>> class Door:
...     def close(self) -> None:
...         print("bang")
...
>>> isinstance(Door(), Closeable)    # Door never mentions Closeable
True
>>> isinstance(42, Closeable)        # ints have no close()
False
```

## TypedDict

Some data really is a dict, and should stay one: parsed JSON, configuration,
rows from an API. A plain `dict[str, Any]` says nothing about which keys it
has. A `TypedDict` gives it a shape, a fixed set of keys, each with its own
type:

```python
from typing import TypedDict

class User(TypedDict):
    name: str
    age: int
```

A checker then knows `user["age"]` is an `int`, and flags `user["agee"]` as a
missing key. At runtime it is a plain `dict`; the class only exists for the
checker:

```pycon
>>> from typing import TypedDict
>>> class User(TypedDict):
...     name: str
...     age: int
...
>>> u: User = {"name": "Ana", "age": 31}
>>> type(u)
<class 'dict'>
```

## Your turn

In `typed.py`, write the following, with **complete annotations**: every
parameter (except `self`) and every return value of every function and
method. A test checks this, and also checks the behaviour.

- `first(items)`: the first item, or `None` if `items` is empty. It works on
  any sequence (`first("xy")` is `"x"`), and is generic over the item type:
  annotate `items` as a sequence of a `TypeVar`.
- `Stack[T]`: a generic class (inheriting from `Generic[T]`) with `push(item)`,
  `pop()` (returns the most recently pushed item, and raises `IndexError` when
  empty), `peek()` (the top item without removing it, or `None` when empty),
  and `__len__`.
- `SupportsArea`: a runtime-checkable `Protocol` with `area() -> float`, so
  `isinstance(obj, SupportsArea)` is true for any object that has an `area`
  method.
- `total_area(shapes)`: the sum of the areas of an iterable of
  `SupportsArea`; an empty iterable gives `0`.
- `Config`: a `TypedDict` with `host: str`, `port: int`, `debug: bool`.
- `parse_config(raw)`: build a `Config` from a `dict[str, str]` like
  `{"host": "x", "port": "80", "debug": "yes"}`. The port becomes an `int`.
  `debug` is `True` for `"1"`, `"true"` or `"yes"` in any mix of capitals
  (`"Yes"` counts), `False` for anything else, and `False` when the key is
  missing.
