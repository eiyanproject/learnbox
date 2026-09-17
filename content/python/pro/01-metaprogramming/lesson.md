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

Metaprogramming is code that works on code: classes that react to being
subclassed, decorators that rewrite classes, classes built at runtime.
Frameworks use it everywhere (Django models, dataclasses, pytest, SQLAlchemy).
Most application code never should, which is exactly why it is worth knowing
how it works.

## Classes are objects, made by type

```python
class Point:
    x = 0

# is roughly
Point = type("Point", (object,), {"x": 0})
```

`type(name, bases, namespace)` builds a class. `type` is the default
**metaclass**: the class of classes. `type(Point)` is `type`.

## __init_subclass__: react to subclassing

Called on the parent whenever a subclass is created. It covers most things
people used to need a metaclass for, such as registries:

```python
class Command:
    registry = {}

    def __init_subclass__(cls, /, name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        Command.registry[name or cls.__name__.lower()] = cls

class Deploy(Command, name="deploy"): ...
class Status(Command): ...

Command.registry     # {'deploy': Deploy, 'status': Status}
```

Keyword arguments in the class statement are passed to `__init_subclass__`.

## Class decorators

A function that receives a finished class and returns it (usually modified).
`@dataclass` is one:

```python
def add_greeting(cls):
    def greet(self):
        return f"hello from {type(self).__name__}"
    cls.greet = greet
    return cls
```

## Metaclasses

A metaclass customises how the class object itself is **created**. Its
`__new__(mcls, name, bases, namespace)` runs when the `class` statement
executes:

```python
class Meta(type):
    def __new__(mcls, name, bases, ns):
        if "run" not in ns and bases:
            raise TypeError(f"{name} must define run()")
        return super().__new__(mcls, name, bases, ns)

class Task(metaclass=Meta): ...
class Broken(Task): ...     # TypeError at class definition time
```

Reach for a metaclass only when you must control class **creation** or
behaviour of the class object itself (e.g. `__getitem__` on the class, or
`__call__` to control instantiation). Two unrelated metaclasses cannot be
combined, which makes them awkward for libraries.

Rule of thumb: decorator, then `__init_subclass__`, then metaclass, in that
order of preference.

## Introspection helpers

`vars(obj)`, `getattr`/`setattr`/`hasattr`, `inspect.getmembers`,
`cls.__mro__`, `func.__code__`, `inspect.signature`.

## Your turn

In `meta.py`:

- `Plugin`: every subclass is registered in `Plugin.registry` under the `name`
  class keyword, or its lower-cased class name. `Plugin.create(name, *args)`
  instantiates a registered plugin, raising `KeyError` for unknown names.
- `auto_repr(cls)`: a class decorator adding `__repr__` like
  `Point(x=1, y=2)` from the instance attributes, in assignment order
- `make_record(name, fields)`: builds a class at runtime with `type()` whose
  `__init__` takes the fields positionally, uses `__slots__`, and whose
  `__name__` is `name`
- `FinalMeta`: a metaclass; classes created with `final=True`
  (`class A(metaclass=FinalMeta, final=True)`) cannot be subclassed:
  trying raises `TypeError`
