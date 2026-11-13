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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **dataclass** | a class whose `__init__`, `__repr__` and `__eq__` are generated from its fields |
| **boilerplate** | repetitive code that always has the same shape |
| **field** | one piece of a dataclass's data |
| **type annotation** | `name: type` in the class body; it defines a field but is not checked at runtime |
| **`list[str]`** | "a list of strings": the square brackets say what the list holds |
| **type checker** | a separate tool, such as mypy, that reads code and reports type mistakes before it runs |
| **mutable default trap** | one default list shared by every object; dataclasses refuse a plain `[]` |
| **default factory** | a function called to make a fresh default for each new object |
| **frozen** | the object cannot be changed after it is created |
| **hashable** | usable as a dict key or set member; frozen dataclasses are |
| **ordered** | comparable with `<` and friends, field by field as a tuple |
| **slots** | a leaner way to store attributes (Advanced section) |
| **`__post_init__`** | a method the generated `__init__` calls last, to check values or work out derived fields |
| **derived field** | a field computed from the others, such as `fahrenheit` from `celsius` |
| **enum** (enumeration) | a fixed set of named choices, the **members** of a class |
| **member name** / **value** | `DRAFT` / `1` |
| **constant** | a value that does not change, written in capitals by convention |
| **sort key** | the one value used for ordering, here built so the highest priority sorts first |
| **cents** | money stored as a whole number of the smallest unit, avoiding float errors |
| **currency** | the kind of money, such as `"EUR"` |

### Python names and functions

| Name | What it does |
|---|---|
| `from dataclasses import dataclass, field` | brings in the decorator and the field helper |
| `@dataclass` | generates the methods |
| `@dataclass(frozen=True)`, `(order=True)`, `(slots=True)` | immutable; orderable; leaner instances |
| `field(default_factory=list)` | a new empty list for each object |
| `field(compare=False)`, `field(repr=False)`, `field(init=False)` | leave the field out of comparisons; of the repr; of `__init__` |
| `object.__setattr__(self, "name", value)` | sets a field on a frozen object, used only in `__post_init__` |
| `dataclasses.replace(obj, field=value)` | a modified copy of a frozen object |
| `from enum import Enum, auto, IntEnum, StrEnum` | the enum tools |
| `auto()` | picks member values for you, counting from 1 |
| `member.name`, `member.value` | the member's name; its value |
| `Status["DRAFT"]`, `Status(1)` | look up a member by name; by value |
| `list(Status)` | all members, in order |
| `is`, `==` | compare members (a plain `Enum` member is not equal to its value) |
| `IntEnum`, `StrEnum` | members that also behave as ints; as strings |
| `__add__(self, other)` | the method `a + b` calls |
| `sorted(...)` | sorts using the generated ordering |

### Errors

| Error | Means |
|---|---|
| `ValueError` | a mutable default without `default_factory`; or a value that `__post_init__` rejects |
| `FrozenInstanceError` | assigning to a field of a frozen dataclass |
| `AttributeError` | a member name that does not exist, such as a typo |
| `TypeError` | comparing plain `Enum` members with `<` |

---

## @dataclass

You wrote `__init__`, `__repr__` and `__eq__` by hand in the Classes lesson.
For a class that mainly holds data, those methods are always the same shape:
store each argument, show each field, compare each field. Writing them out is
repetitive and easy to get subtly wrong, for example by adding a field and
forgetting to add it to `__eq__`. The `dataclasses` module generates them
for you from a list of the fields.

Each field is written as a **type annotation**: a name, a colon, and the type
the field should hold, optionally followed by `=` and a default. The
`@dataclass` decorator reads those lines and writes the methods:

```pycon
>>> from dataclasses import dataclass, field
>>> @dataclass
... class Book:
...     title: str
...     author: str
...     pages: int = 0
...     tags: list[str] = field(default_factory=list)
...
>>> b = Book("Dune", "Herbert", 412)
>>> b
Book(title='Dune', author='Herbert', pages=412, tags=[])
>>> b == Book("Dune", "Herbert", 412)
True
```

What you got without writing them: an `__init__` that takes the fields in
order (`pages` and `tags` are optional because they have defaults), a
`__repr__` that shows every field by name, and an `__eq__` that compares all
the fields. `list[str]` means "a list of strings"; the square brackets say
what the list holds.

- The annotations define the fields, in order. Fields with defaults must come
  after fields without, for the same reason as function parameters with
  defaults.
- The annotation is not enforced at runtime. Python does not check that
  `title` really is a `str`; the annotations are documentation, and the input
  for a **type checker** (a separate tool, such as mypy, that reads your code
  and reports type mistakes before you run it):

  ```pycon
  >>> Book(1, 2, "x")          # accepted, although none of these types match
  Book(title=1, author=2, pages='x', tags=[])
  ```

- Never write `tags: list[str] = []`. A plain `[]` default would be one list
  shared by every `Book`, the mutable-default trap from the Functions lesson,
  and dataclasses refuse it outright:

  ```pycon
  >>> @dataclass
  ... class Bad:
  ...     tags: list = []
  ...
  Traceback (most recent call last):
    ...
  ValueError: mutable default <class 'list'> for field tags is not allowed: use default_factory
  ```

  Use `field(default_factory=list)` instead. `default_factory` takes a
  function, which is called to make a fresh default for each new object, the
  same idea as `defaultdict(list)`.

## Options

`@dataclass` takes arguments that switch on extra behaviour:

```python
@dataclass(frozen=True)     # immutable: assigning a field raises; instances are hashable
@dataclass(order=True)      # <, <=, >, >= compare fields as a tuple, in order
@dataclass(slots=True)      # smaller, faster instances (see the Advanced section)
```

(These are three separate options, shown one per line; you can combine them
in one call, such as `@dataclass(frozen=True, order=True)`.)

**Frozen** instances cannot be changed after they are created. Because they
cannot change, they are **hashable**: they can be used as dict keys and
stored in sets, like tuples and strings. **Ordered** instances can be sorted,
comparing the first field, then the second on a tie, and so on:

```pycon
>>> from dataclasses import FrozenInstanceError
>>> @dataclass(frozen=True, order=True)
... class Version:
...     major: int
...     minor: int
...
>>> v = Version(1, 4)
>>> v.minor = 5
Traceback (most recent call last):
  ...
dataclasses.FrozenInstanceError: cannot assign to field 'minor'
>>> sorted([Version(2, 0), Version(1, 9), Version(1, 10)])
[Version(major=1, minor=9), Version(major=1, minor=10), Version(major=2, minor=0)]
>>> {Version(1, 4): "stable"}[v]       # usable as a dict key
'stable'
```

Note that 1.10 sorts after 1.9 here, because the fields are compared as
numbers, which is what you want for version numbers and would not get from
comparing strings.

`field()` tunes single fields:

- `field(compare=False)` leaves the field out of `==` and of the ordering.
- `field(repr=False)` leaves it out of the printed `repr`.
- `field(init=False)` leaves it out of `__init__`, so it cannot be passed in;
  something else, usually `__post_init__`, must set it.

## __post_init__

The generated `__init__` only stores the arguments. If you need more, such
as checking that the values make sense or working out a field from the
others, write a `__post_init__` method. The generated `__init__` calls it as
its last step:

```pycon
>>> @dataclass
... class Temperature:
...     celsius: float
...     fahrenheit: float = field(init=False)
...
...     def __post_init__(self):
...         if self.celsius < -273.15:
...             raise ValueError("below absolute zero")
...         self.fahrenheit = self.celsius * 9 / 5 + 32
...
>>> Temperature(100)
Temperature(celsius=100, fahrenheit=212.0)
>>> Temperature(-300)
Traceback (most recent call last):
  ...
ValueError: below absolute zero
```

`fahrenheit` has `init=False`, so `Temperature(100)` takes only the Celsius
value, and `__post_init__` fills in the other.

For a frozen dataclass, normal assignment in `__post_init__` raises, the same
as anywhere else, because the object is already frozen by then. It has to use
`object.__setattr__(self, "name", value)`, which goes around the dataclass's
block on assignment. Use it only there, while setting the object up.

Frozen instances are "changed" by making a modified copy:
`dataclasses.replace(v, minor=5)` returns a new `Version(1, 5)` and leaves
`v` alone, like `_replace` on a namedtuple.

## Enum

Many values can only be one of a few fixed choices: an order's status, a
day of the week, a priority. You could use strings, but `status == "publshed"`
with a typo is silently false, and nothing stops `"pubished"` being stored.
An **enum** (short for enumeration) names a fixed set of choices as members
of a class, so a typo becomes an immediate `AttributeError` instead of a
silent bug:

```pycon
>>> from enum import Enum, auto
>>> class Status(Enum):
...     DRAFT = auto()
...     PUBLISHED = auto()
...     ARCHIVED = auto()
...
>>> s = Status.DRAFT
>>> s.name
'DRAFT'
>>> s.value              # auto() numbers from 1
1
>>> Status["DRAFT"]      # look up by name
<Status.DRAFT: 1>
>>> Status(1)            # look up by value
<Status.DRAFT: 1>
>>> s is Status.DRAFT    # compare with `is` or ==
True
>>> list(Status)         # all members, in order
[<Status.DRAFT: 1>, <Status.PUBLISHED: 2>, <Status.ARCHIVED: 3>]
```

Each member has a **name** (`DRAFT`) and a **value** (`1`). `auto()` picks
the values for you, counting from 1, when the exact numbers do not matter;
you can also write values yourself, such as `DRAFT = 1`. Members are written
in capitals by convention, because they are constants. There is exactly one
`Status.DRAFT` object, so `is` and `==` both work for comparing members.

And the typo:

```pycon
>>> Status.PUBLSHED
Traceback (most recent call last):
  ...
AttributeError: ...PUBLSHED...
```

(The exact wording varies between Python versions; recent ones say the
class has no attribute `PUBLSHED` and suggest `PUBLISHED`.)

A plain `Enum` member is not equal to its value: `Status.DRAFT == 1` is
`False`. That is deliberate, so enum members do not get mixed up with
ordinary numbers. When you do want them to act like numbers or strings, for
example to compare with values from a database, use `IntEnum` (members also
behave as ints) or `StrEnum` (members also behave as strings):

```pycon
>>> from enum import IntEnum
>>> class Level(IntEnum):
...     LOW = 1
...     HIGH = 3
...
>>> Level.HIGH == 3, Level.HIGH > Level.LOW
(True, True)
```

## Your turn

In `models.py`:

- `Priority`: an `Enum` with `LOW = 1`, `MEDIUM = 2`, `HIGH = 3`
- `Task`: a dataclass with these fields:

  | Field | Type | Default |
  |---|---|---|
  | `title` | `str` | none: it is required |
  | `priority` | `Priority` | `Priority.MEDIUM` |
  | `tags` | `list[str]` | an empty list, a new one for every task |
  | `done` | `bool` | `False` |

  A sorted list of tasks must come out **highest priority first**, and by
  title where the priority is equal. To get that, add one more field,
  `sort_key`, and make it the only field that is compared. It is not an
  `__init__` argument and does not appear in the `repr`; `__post_init__`
  sets it, to a value that sorts the way the tasks should. Every other field
  is left out of comparisons.

  A plain `Enum` member cannot be compared with `<`, so the key has to be
  built from something that can, such as the member's `.value`. A tuple key
  sorts by its first part, then its second, and negating a number reverses
  its order, which are the two tricks from the Functions in depth lesson.
- `Money`: a frozen dataclass with `amount: int` (in cents) and
  `currency: str`. Creating one with a negative amount raises `ValueError`.
  `a + b` returns a new `Money` holding the sum, and raises `ValueError` when
  the two currencies differ. `+` calls a method named `__add__(self, other)`,
  so that is the method to write; it returns the new object rather than
  changing either side, which a frozen class could not do anyway.
