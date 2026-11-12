---
title: Inheritance, properties and ABCs
summary: super() and the MRO, properties with validation, class and static methods, and abstract base classes.
order: 1
files: [shapes.py]
run: python -i shapes.py
hints:
  - "`Shape(ABC)` declares `@abstractmethod def area(self)` and `perimeter`. `describe` is a normal method using them."
  - "`Rectangle.width` is a `@property` returning `self._width`, with a `@width.setter` that raises `ValueError` for non-positive values and then stores it."
  - "`Square.__init__(self, side)` calls `super().__init__(side, side)`. `from_area` is a `@classmethod` returning `cls(math.sqrt(area))`."
  - "`Square` keeps its sides equal by overriding the setters: `@Rectangle.width.setter def width(self, v): Rectangle.width.fset(self, v); Rectangle.height.fset(self, v)` (and the same for height)."
---

The Beginner section introduced classes and a first taste of inheritance.
This lesson covers the tools that make class hierarchies hold up in real
code: how `super()` really decides which method runs, attributes that check
their own values, methods that belong to the class rather than to an
instance, and abstract base classes that make a forgotten method an
immediate error instead of a surprise later on.

## Inheritance and super()

A subclass reuses and extends its parent. It inherits every method it does
not define itself, and **overrides** the ones it does:

```pycon
>>> class Animal:
...     def __init__(self, name):
...         self.name = name
...     def speak(self):
...         return "..."
...     def introduce(self):
...         return f"{self.name} says {self.speak()}"
...
>>> class Dog(Animal):
...     def __init__(self, name, breed):
...         super().__init__(name)      # let the parent do its part
...         self.breed = breed
...     def speak(self):                # override
...         return "Woof"
...
>>> rex = Dog("Rex", "collie")
>>> rex.introduce()
'Rex says Woof'
>>> rex.name, rex.breed
('Rex', 'collie')
```

`Dog` has no `introduce` of its own, so the one from `Animal` runs. Inside
it, `self.speak()` looks the method up on the actual object, which is a
`Dog`, so it gets `Dog`'s `speak`. This is the point of overriding: code
written in the parent automatically uses the subclass's version.

`Dog.__init__` replaces `Animal.__init__`, so without the `super()` call,
`self.name` would never be set. `super().__init__(name)` runs the parent's
setup, and `Dog` then adds its own part.

`super()` does not literally mean "my parent". It means "the next class in
the **method resolution order**", the list described in the next section.
With single inheritance (one parent each) that is always the parent. With
multiple inheritance it can be a sibling class, and that is what lets
several classes each add their part to the same method, each calling
`super()` to pass control on.

## The MRO

A class can inherit from more than one parent: `class D(B, C)`. Then a
method could come from several places, and Python needs a fixed order to
search them. That order is the **method resolution order** (MRO), and every
class keeps it in `__mro__`:

```pycon
>>> class A: ...
>>> class B(A): ...
>>> class C(A): ...
>>> class D(B, C): ...
>>> [cls.__name__ for cls in D.__mro__]
['D', 'B', 'C', 'A', 'object']
```

Attribute lookup walks this list from the left and stops at the first class
that has the name. Python computes the order with an algorithm called C3
linearisation, which guarantees two rules: a class always comes before its
parents, and parents keep the order they were listed in. So `B` comes before
`C` (listed first), and `A` comes after both (it is their parent), even though
`B` inherits from it directly. `object` is the root of every class and always
comes last.

When you are unsure which method will run in a hierarchy, print `__mro__`
rather than guessing.

## Properties

You often start a class with a plain attribute, `self.balance = 0`, and
later need to check every value assigned to it. Changing every caller to use
a `set_balance()` method would be a lot of churn. A **property** looks like
an attribute from the outside but runs a method on every read or write, so
you can add validation later without changing any caller:

```pycon
>>> class Account:
...     def __init__(self, balance):
...         self.balance = balance          # goes through the setter
...
...     @property
...     def balance(self):
...         return self._balance
...
...     @balance.setter
...     def balance(self, value):
...         if value < 0:
...             raise ValueError("balance cannot be negative")
...         self._balance = value
...
>>> acc = Account(10)
>>> acc.balance             # runs the first method, the getter
10
>>> acc.balance = 25        # runs the setter
>>> acc.balance = -5
Traceback (most recent call last):
  ...
ValueError: balance cannot be negative
>>> acc.balance             # the bad value was never stored
25
```

How it fits together:

- `@property` above `def balance(self)` turns the method into a property.
  Reading `acc.balance` calls it, with no brackets at the call site.
- `@balance.setter` above a second `def balance(self, value)` adds the
  method that runs on assignment, `acc.balance = ...`. Both methods must
  have the same name as the property.
- The value itself is stored under a different name, `_balance`. It has to
  be: `self.balance = value` inside the setter would call the setter again,
  forever.
- Even the assignment in `__init__` goes through the setter, so an
  `Account(-1)` is rejected at creation too.

A property with no setter is read-only: assigning to it raises
`AttributeError`. The leading underscore on `_balance` is the Python
convention for "internal, do not touch from outside the class". Nothing
enforces it; it is a signal to other programmers.

## classmethod and staticmethod

Normal methods receive the instance as `self`. Two decorators change that:

```pycon
>>> class Date:
...     def __init__(self, y, m, d):
...         self.y, self.m, self.d = y, m, d
...
...     @classmethod
...     def from_iso(cls, text):            # alternative constructor
...         return cls(*map(int, text.split("-")))
...
...     @staticmethod
...     def is_leap(year):                  # a plain function that lives on the class
...         return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
...
>>> d = Date.from_iso("2026-09-18")
>>> d.y, d.m, d.d
(2026, 9, 18)
>>> Date.is_leap(2024)
True
```

- A **class method** receives the class itself as its first argument,
  called `cls` by convention, instead of an instance. Its most common use is
  an **alternative constructor**: another way to build an object, here from a
  string such as `"2026-09-18"`. `text.split("-")` gives
  `["2026", "09", "18"]`, `map(int, ...)` converts each to a number, and `*`
  spreads them out as the three arguments to `cls(...)`.
- A **static method** receives neither the instance nor the class. It is an
  ordinary function that lives in the class's namespace because it belongs
  with the class logically, and is called as `Date.is_leap(2024)`.

`cls` is the class the method was *called on*, so `SubDate.from_iso(...)` on a
subclass builds a `SubDate`. That only works if the method builds with
`cls(...)`; writing `Date(...)` inside it would always produce a plain `Date`,
even for subclasses. So always build with `cls(...)`, not the hard-coded class
name.

## Abstract base classes

Sometimes a base class exists only to say what its subclasses must provide:
"every storage backend has a `save` method". An **abstract base class**
(ABC) declares such an interface. Methods marked `@abstractmethod` have no
real implementation in the base class; every concrete subclass must
override them. A class with any unimplemented `@abstractmethod` cannot be
instantiated:

```pycon
>>> from abc import ABC, abstractmethod
>>> class Storage(ABC):
...     @abstractmethod
...     def save(self, key, data): ...
...
...     def save_all(self, items):      # concrete method built on the abstract one
...         for k, v in items.items():
...             self.save(k, v)
...
>>> Storage()
Traceback (most recent call last):
  ...
TypeError: Can't instantiate abstract class Storage...
```

A subclass that fills in `save` can be created, and it gets `save_all` for
free:

```pycon
>>> class MemoryStorage(Storage):
...     def __init__(self):
...         self.data = {}
...     def save(self, key, data):
...         self.data[key] = data
...
>>> m = MemoryStorage()
>>> m.save_all({"a": 1, "b": 2})
>>> m.data
{'a': 1, 'b': 2}
```

The check happens at construction time. If a subclass forgets one of the
abstract methods, the mistake shows up the moment someone tries to create
one, with a message naming the missing method, rather than much later, deep
in some other code, when the missing method is finally called.

## Composition over inheritance

Inheritance says "is a": a `Dog` is an `Animal`, and can be used anywhere an
`Animal` is expected. If the honest relationship is "has a", give the class
an attribute holding the other object instead. That is **composition**. A
`Car` that *has* an `Engine` (`self.engine = Engine()`) can be tested with a
fake engine and can swap engines later; a `Car` that *is* an `Engine` cannot.
Deep inheritance hierarchies are hard to change, because a change to a class
near the top ripples through everything below it. Reach for inheritance when
a subclass really is a special kind of its parent, and for composition the
rest of the time.

## Your turn

In `shapes.py`:

- `Shape`: an ABC with abstract `area()` and `perimeter()`, and a concrete
  `describe()` returning text like `"Rectangle area=12.00 perimeter=14.00"`:
  the name of the object's actual class (`type(self).__name__`), then both
  numbers with exactly 2 decimals. A subclass that does not provide both
  methods must not be creatable.
- `Rectangle(width, height)`: a `Shape`. `width` and `height` are properties
  (a test checks that `width` really is a `property` on `Rectangle`) that
  reject values `<= 0` with `ValueError`, including in `__init__`. A rejected
  value must leave the old one in place.
- `Square(side)`: a `Rectangle` whose sides always stay equal: setting either
  `width` or `height` sets both. `Square.from_area(area)` is a classmethod
  that builds a square with that area (side = square root of the area), and
  on a subclass of `Square` it must build that subclass.
- `Circle(radius)`: a `Shape` with `radius` validated the same way. Its
  perimeter is the circumference, `2 * math.pi * radius`.
