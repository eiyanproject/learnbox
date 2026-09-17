---
title: Dataclasses and enums
summary: Let @dataclass write the boilerplate, make records immutable or orderable, and name fixed choices with Enum.
order: 6
files: [models.py]
run: python -i models.py
hints:
  - "`Priority(Enum)` with `LOW = 1`, `MEDIUM = 2`, `HIGH = 3`."
  - "`@dataclass(order=True)` compares fields in the order they are declared, so put `sort_key` first and exclude the rest with `field(compare=False)`."
  - "Mutable defaults need `field(default_factory=list)`. The derived `sort_key` uses `field(init=False, repr=False)` and is set in `__post_init__`."
  - "`Money` is `@dataclass(frozen=True)`; `__add__` checks the currency and returns a new `Money`."
---

## @dataclass

You wrote `__init__`, `__repr__` and `__eq__` by hand in the Classes lesson.
For classes that mainly hold data, `dataclasses` generates them from type
annotations:

```python
from dataclasses import dataclass, field

@dataclass
class Book:
    title: str
    author: str
    pages: int = 0
    tags: list[str] = field(default_factory=list)

b = Book("Dune", "Herbert", 412)
b                 # Book(title='Dune', author='Herbert', pages=412, tags=[])
b == Book("Dune", "Herbert", 412)    # True
```

- The annotations define the fields, in order. Fields with defaults must come
  after fields without.
- The annotation is not enforced at runtime. `Book(1, 2, "x")` works; it is
  documentation, and a type checker's input.
- Never write `tags: list = []`: dataclasses refuse it, for the same
  mutable-default reason as functions. Use `field(default_factory=list)`.

## Options

```python
@dataclass(frozen=True)     # immutable: assigning a field raises; instances are hashable
@dataclass(order=True)      # <, <=, >, >= compare fields as a tuple, in order
@dataclass(slots=True)      # smaller, faster instances (see the Advanced track)
```

`field()` tunes single fields: `field(compare=False)`, `field(repr=False)`,
`field(init=False)`.

## __post_init__

Runs after the generated `__init__`: validate, or compute derived fields.

```python
@dataclass
class Temperature:
    celsius: float
    fahrenheit: float = field(init=False)

    def __post_init__(self):
        if self.celsius < -273.15:
            raise ValueError("below absolute zero")
        self.fahrenheit = self.celsius * 9 / 5 + 32
```

For a frozen dataclass, `__post_init__` has to use
`object.__setattr__(self, "name", value)`.

Frozen instances are "changed" by making a copy: `dataclasses.replace(p, x=5)`.

## Enum

An **enum** names a fixed set of choices, so typos become errors instead of
silent bugs:

```python
from enum import Enum, auto

class Status(Enum):
    DRAFT = auto()
    PUBLISHED = auto()
    ARCHIVED = auto()

s = Status.DRAFT
s.name            # 'DRAFT'
s.value           # 1
Status["DRAFT"]   # look up by name
Status(1)         # look up by value
s is Status.DRAFT # compare with `is` or ==
list(Status)      # all members, in order
```

`IntEnum` members also behave as ints; `StrEnum` members as strings.

## Your turn

In `models.py`:

- `Priority`: an `Enum` with `LOW = 1`, `MEDIUM = 2`, `HIGH = 3`
- `Task`: a dataclass with `title: str`, `priority: Priority = Priority.MEDIUM`,
  `tags: list[str]` (default empty, never shared between tasks) and `done: bool = False`.
  Tasks must sort **highest priority first**, then by title. Add a
  `sort_key` field that is not an `__init__` argument, not shown in `repr`, set
  in `__post_init__`, and is the only thing compared.
- `Money`: a frozen dataclass with `amount: int` (cents) and `currency: str`.
  Negative amounts raise `ValueError`. `a + b` returns a new `Money`, and raises
  `ValueError` when currencies differ.
