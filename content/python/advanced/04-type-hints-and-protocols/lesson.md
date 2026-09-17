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

Type hints describe what a function expects and returns. Python ignores them at
runtime; tools use them: editors for completion, and type checkers such as
`mypy` or `pyright` to find bugs before the code runs.

```python
def greet(name: str, times: int = 1) -> str:
    return f"hi {name} " * times

count: int = 0
names: list[str] = []
scores: dict[str, float] = {}
maybe: int | None = None
```

Annotations are stored on the object: `greet.__annotations__`, or
`typing.get_type_hints(greet)`.

## The useful vocabulary

```python
from typing import Any, Callable, Iterable, Iterator, Literal, Sequence, TypeVar

def total(xs: Iterable[float]) -> float: ...            # accept any iterable, not just list
def apply(f: Callable[[int], str], x: int) -> str: ...
Mode = Literal["r", "w", "a"]                            # only these values
def open_file(path: str, mode: Mode = "r") -> None: ...
```

Accept the most general type you can (`Iterable`, `Sequence`, `Mapping`) and
return the most specific one (`list[str]`).

## Generics

A `TypeVar` links types together: "whatever type goes in, that same type comes out":

```python
T = TypeVar("T")

def last(items: Sequence[T]) -> T:
    return items[-1]

last([1, 2, 3])      # a checker knows this is int
last("abc")          # and this is str
```

Classes too:

```python
from typing import Generic

class Box(Generic[T]):
    def __init__(self, item: T) -> None:
        self.item = item

    def get(self) -> T:
        return self.item
```

(Python 3.12 adds the shorter `def last[T](items: Sequence[T]) -> T` and
`class Box[T]:` syntax.)

## Protocol: structural typing

An ABC requires subclasses to inherit from it. A **Protocol** only requires the
right methods. That matches how Python code is actually written ("duck typing"):

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...

def shutdown(things: list[Closeable]) -> None:
    for t in things:
        t.close()
```

Files, sockets and your own classes all satisfy `Closeable` without knowing it
exists. `@runtime_checkable` also allows `isinstance(x, Closeable)` (which
checks only that the methods exist).

## TypedDict

When data really is a dict (JSON, config), give it a shape:

```python
from typing import TypedDict

class User(TypedDict):
    name: str
    age: int
```

At runtime it is a plain `dict`.

## Your turn

In `typed.py`, fully annotated:

- `first(items)`: the first item or `None`, generic over the item type
- `Stack[T]`: `push`, `pop` (raises `IndexError` when empty), `peek` (or
  `None`), `__len__`
- `SupportsArea`: a runtime-checkable `Protocol` with `area() -> float`
- `total_area(shapes)`: sum of areas of an iterable of `SupportsArea`
- `Config`: a `TypedDict` with `host: str`, `port: int`, `debug: bool`
- `parse_config(raw)`: from a `dict[str, str]` like `{"host": "x", "port": "80", "debug": "yes"}`

The tests check behaviour and that every function and method has complete annotations.
