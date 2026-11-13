---
title: Metaprogramming
summary: Classes that register themselves, class decorators, building classes with type(), and when a metaclass is really needed.
order: 1
files: [meta.py]
run: python -i meta.py
hints:
  - "`Plugin.__init_subclass__(cls, /, name=None, **kwargs)`: call `super().__init_subclass__(**kwargs)`, then `Plugin.registry[name or cls.__name__.lower()] = cls`."
  - "`auto_repr(cls)` builds a `__repr__` that reads `vars(self)`, attaches it with `cls.__repr__ = __repr__`, and returns `cls`."
  - "`make_record(name, fields)`: build the `__init__` with `zip(fields, args)` and `setattr`, then `return type(name, (), {\"__init__\": __init__, \"__slots__\": tuple(fields)})`."
  - "`FinalMeta.__new__(mcls, name, bases, ns)`: loop over `bases`; if any is an instance of `FinalMeta` with `getattr(base, \"_final\", False)`, raise `TypeError`. Otherwise `return super().__new__(mcls, name, bases, ns)`."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **metaprogramming** | code that works on code: classes that react to subclassing, decorators that rewrite classes, classes built at runtime |
| **framework** | a library that runs your code within its own structure, such as Django, pytest or SQLAlchemy |
| **class object** | what a `class` statement produces when it runs, stored under the class's name |
| **base class** | a parent class, listed in a tuple when building a class with `type` |
| **namespace** | the dict of everything defined in a class body |
| **metaclass** | the class of a class; it decides how a class is created and behaves; `type` is the default |
| **registry** | a dict that notes down classes automatically so the program can find them by name |
| **class keyword** | a keyword in the class statement, after the bases: `class Deploy(Command, name="deploy")` |
| **class decorator** | a function that receives a finished class and returns it, usually modified |
| **`mcls`** | the conventional name for a metaclass inside its own methods |
| **metaclass conflict** | the error when a class would need two unrelated metaclasses |
| **introspection** | a program examining its own objects while it runs |
| **final class** | a class that cannot be subclassed |
| **record class** | a simple class holding a fixed set of fields |

### Python names and functions

| Name | What it does |
|---|---|
| `type(name, bases, namespace)` | builds a class from a name, a tuple of bases and a dict |
| `type(obj)` | an object's type (the one-argument form) |
| `__init_subclass__(cls, /, name=None, **kwargs)` | called on the parent whenever a subclass is created; automatically a class method |
| `super().__init_subclass__(**kwargs)` | passes other keywords on up the hierarchy |
| `cls.__name__.lower()` | the class's name in lower case |
| `cls.greet = greet` | adds a method to a class after it was created |
| `class Meta(type):` | defines a metaclass |
| `__new__(mcls, name, bases, ns)` | runs when a `class` statement executes; can change or refuse the class |
| `class Task(metaclass=Meta):` | chooses a metaclass |
| `vars(obj)` | an object's own attributes as a dict, in assignment order |
| `getattr`, `setattr`, `hasattr` | read, write, test an attribute whose name is in a string |
| `cls.__mro__` | the method resolution order |
| `inspect.signature(func)` | a function's parameters, defaults and annotations |
| `inspect.getmembers(obj)` | every attribute as `(name, value)` pairs |
| `__slots__` | the fixed set of allowed attributes |
| `zip(fields, args)` | pairs each field name with its argument |

### Errors

| Error | Means |
|---|---|
| `TypeError` | a metaclass refused the class, wrong number of arguments, or subclassing a final class |
| `KeyError` | an unknown plugin name |

---

**Metaprogramming** is code that works on code: classes that react to being
subclassed, decorators that rewrite classes, classes built while the program
runs. You have already used its results. `@dataclass` reads a class's
annotations and writes methods into it; Django models, pytest and SQLAlchemy
use the same techniques to turn a few lines of declarations into working
machinery.

Most application code never should do this. It makes code harder to read,
because behaviour comes from somewhere other than the lines in front of you.
That is exactly why it is worth knowing how it works: when a framework does
something surprising, these are the mechanisms behind it, and when you do
need one, you should reach for the simplest that does the job.

## Classes are objects, made by type

A `class` statement is not a declaration that exists before the program
runs. It is a statement that runs, top to bottom, and produces an object,
the class, which is then stored under the class's name. Like every object,
a class has a type, and that type is `type`:

```python
class Point:
    x = 0

# is roughly
Point = type("Point", (object,), {"x": 0})
```

`type(name, bases, namespace)` with three arguments builds a class: the
name as a string, a tuple of base classes, and a dict of everything defined
in the class body. (With one argument, `type(obj)` tells you an object's
type, as you have used all along; the three-argument form is the same
built-in doing a different job.)

```pycon
>>> Point = type("Point", (object,), {"x": 0, "double": lambda self: self.x * 2})
>>> p = Point()
>>> p.x, p.double()
(0, 0)
>>> type(p) is Point, type(Point) is type
(True, True)
```

Because `type` makes classes, it is called the default **metaclass**: the
class of classes. An instance's class decides how the instance behaves; a
class's metaclass decides how the class behaves, and how it is created.

## __init_subclass__: react to subclassing

A common need: every subclass of some base should be noted down
automatically, so the program can find all the available commands, plugins
or file formats without a hand-maintained list. `__init_subclass__` is a
method on the parent class that Python calls whenever a subclass of it is
created, with the new subclass as `cls`. It covers most things people used to
need a metaclass for, such as registries:

```pycon
>>> class Command:
...     registry = {}
...
...     def __init_subclass__(cls, /, name=None, **kwargs):
...         super().__init_subclass__(**kwargs)
...         Command.registry[name or cls.__name__.lower()] = cls
...
>>> class Deploy(Command, name="deploy"): ...
>>> class Status(Command): ...
>>> Command.registry
{'deploy': <class '__main__.Deploy'>, 'status': <class '__main__.Status'>}
```

Merely defining `Deploy` and `Status` registered them; nothing else had to
call anything.

- Keyword arguments in the class statement, like `name="deploy"` after the
  bases, are passed to `__init_subclass__`. `Status` gives none, so `name` is
  `None` and the lower-cased class name is used instead.
- `__init_subclass__` is automatically a class method: its first argument
  is the new subclass, not an instance.
- The `/` makes `cls` positional-only, so a subclass keyword can never
  clash with it, and `**kwargs` passed on to `super()` lets other classes in
  the hierarchy receive keywords meant for them. Both are good habits.
- The registry is written as `Command.registry`, not `cls.registry`, so every
  subclass registers into the one shared dict on the base class.

The registry can then create objects by name, which is how a command-line
tool might map the word a user typed to a class:
`Command.registry["deploy"]()` creates a `Deploy`.

## Class decorators

You have seen decorators that wrap functions. A **class decorator** is a
function that receives a finished class, after the `class` statement has
run, and returns it, usually modified. `@dataclass` is one:

```python
def add_greeting(cls):
    def greet(self):
        return f"hello from {type(self).__name__}"
    cls.greet = greet
    return cls
```

```pycon
>>> def add_greeting(cls):
...     def greet(self):
...         return f"hello from {type(self).__name__}"
...     cls.greet = greet
...     return cls
...
>>> @add_greeting
... class Robot:
...     pass
...
>>> Robot().greet()
'hello from Robot'
```

`cls.greet = greet` adds a method to the class after it was created; a
function assigned to a class attribute becomes a method like any other. The
decorator must `return cls`, or the name `Robot` would end up as `None`.

Class decorators are the simplest tool here: plain functions, applied
visibly, with no effect on subclasses unless those are decorated too.

## Metaclasses

A **metaclass** customises how the class object itself is **created**. You
write one by subclassing `type`, and choose it with `metaclass=` in the class
statement. Its `__new__(mcls, name, bases, namespace)` runs when the `class`
statement executes, receiving the same three things as `type(name, bases,
namespace)`, and it can inspect or change them, or refuse to create the
class at all:

```pycon
>>> class Meta(type):
...     def __new__(mcls, name, bases, ns):
...         if "run" not in ns and bases:
...             raise TypeError(f"{name} must define run()")
...         return super().__new__(mcls, name, bases, ns)
...
>>> class Task(metaclass=Meta): ...
>>> class Broken(Task): ...     # fails as the class is defined, not when used
Traceback (most recent call last):
  ...
TypeError: Broken must define run()
```

`mcls` is the metaclass itself (by convention, the way `cls` is used for a
class). `Task` has no bases, so the check is skipped for it. `Broken`
inherits from `Task`, so it gets the same metaclass, and its namespace
`ns` has no `run`, so creating it fails at once.

A metaclass is inherited: every subclass of a class with a metaclass is made
by that metaclass too. Keyword arguments in the class statement reach the
metaclass's `__new__` as well (after `ns`), which is how this lesson's
`final=True` exercise works.

Reach for a metaclass only when you must control class **creation**, or the
behaviour of the class object itself: for example `__getitem__` on the class
(so `MyClass[...]` does something), or `__call__` to control what
`MyClass(...)` does when it creates instances. A class can only have one
metaclass, and two unrelated metaclasses cannot be combined, which makes
them awkward for libraries: a user's class that mixes in two libraries'
bases, each with its own metaclass, fails with a "metaclass conflict" error.

Rule of thumb: class decorator, then `__init_subclass__`, then metaclass, in
that order of preference. Use the first one that can do the job.

## Introspection helpers

**Introspection** means a program examining its own objects while it runs.
These are the everyday tools for it:

- `vars(obj)`: an object's own attributes, as a dict (its `__dict__`).
- `getattr(obj, "name")`, `setattr(obj, "name", value)`, `hasattr(obj,
  "name")`: read, write or test an attribute whose name is in a string,
  which is how code can handle attributes it did not know about in advance.
- `cls.__mro__`: the method resolution order, from the Advanced section.
- `inspect.signature(func)`: a function's parameters, with their defaults
  and annotations.
- `inspect.getmembers(obj)`: every attribute, as `(name, value)` pairs.

```pycon
>>> class Pet:
...     def __init__(self):
...         self.name = "Rex"
...         self.age = 3
...
>>> pet = Pet()
>>> vars(pet)
{'name': 'Rex', 'age': 3}
>>> field = "age"
>>> getattr(pet, field)
3
>>> setattr(pet, field, 4)
>>> pet.age
4
>>> import inspect
>>> inspect.signature(lambda a, b=2, *, c: None)
<Signature (a, b=2, *, c)>
```

`vars` keeps the order the attributes were assigned in, which is useful for
building a `repr`.

## Your turn

In `meta.py`:

- `Plugin`: every subclass is registered in `Plugin.registry` under the
  `name` class keyword, or its lower-cased class name if there is none. Use
  `__init_subclass__` (a test checks `Plugin` defines it).
  `Plugin.create(name, *args)` instantiates the registered plugin, passing
  `args` to its constructor, and raises `KeyError` for unknown names.
- `auto_repr(cls)`: a class decorator adding a `__repr__` like
  `Point(x=1, y='a')` from the instance's attributes, in assignment order,
  with each value shown by its `repr` (so strings get quotes). An object with
  no attributes shows as `Empty()`. The decorator must return the class.
- `make_record(name, fields)`: builds a class at runtime with `type()` whose
  `__name__` is `name`, whose `__init__` takes the fields positionally
  (exactly that many arguments; too few raises `TypeError`), and which has
  `__slots__` equal to the tuple of field names, so no other attributes can
  be added.
- `FinalMeta`: a metaclass; classes created with `final=True`
  (`class A(metaclass=FinalMeta, final=True)`, or `class A(Base,
  final=True)` where `Base` uses `FinalMeta`) cannot be subclassed: trying
  raises `TypeError` when the subclass is defined. Classes without
  `final=True` can be subclassed as normal.
