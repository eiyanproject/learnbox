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

## Inheritance and super()

A subclass reuses and extends its parent:

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)      # let the parent do its part
        self.breed = breed

    def speak(self):                # override
        return "Woof"
```

`super()` does not mean "my parent". It means "the next class in the **method
resolution order**". With single inheritance that is the parent; with multiple
inheritance it is what makes cooperative classes work.

## The MRO

```python
class A: ...
class B(A): ...
class C(A): ...
class D(B, C): ...

D.__mro__     # (D, B, C, A, object)
```

Attribute lookup walks this list. Python computes it with C3 linearisation:
children before parents, and parents in the order listed.

## Properties

A property looks like an attribute but runs code, so you can add validation
later without changing any caller:

```python
class Account:
    def __init__(self, balance):
        self.balance = balance          # goes through the setter

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("balance cannot be negative")
        self._balance = value
```

A property with no setter is read-only. The leading underscore on `_balance` is
the convention for "internal, do not touch".

## classmethod and staticmethod

```python
class Date:
    def __init__(self, y, m, d): ...

    @classmethod
    def from_iso(cls, text):            # alternative constructor
        return cls(*map(int, text.split("-")))

    @staticmethod
    def is_leap(year):                  # just a function that lives on the class
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

`cls` is the class the method was called on, so `SubDate.from_iso(...)` builds a
`SubDate`. Always build with `cls(...)`, not the hard-coded class name.

## Abstract base classes

An ABC defines an interface that subclasses must fill in. A class with any
unimplemented `@abstractmethod` cannot be instantiated:

```python
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def save(self, key, data): ...

    def save_all(self, items):          # concrete method built on the abstract one
        for k, v in items.items():
            self.save(k, v)

Storage()        # TypeError: Can't instantiate abstract class Storage
```

This catches a forgotten method at construction time rather than much later,
when the missing method is finally called.

## Composition over inheritance

Inheritance says "is a". If the honest relationship is "has a", give the class
an attribute instead. Deep hierarchies are hard to change; a `Car` that *has* an
`Engine` is easier to test than one that *is* one.

## Your turn

In `shapes.py`:

- `Shape`: an ABC with abstract `area()` and `perimeter()`, and a concrete
  `describe()` returning `"Rectangle area=12.00 perimeter=14.00"` (using the
  class name)
- `Rectangle(width, height)`: `width` and `height` are properties that reject
  values `<= 0` with `ValueError`, including in `__init__`
- `Square(side)`: a `Rectangle` whose sides always stay equal: setting either
  `width` or `height` sets both. `Square.from_area(area)` is a classmethod.
- `Circle(radius)`: a `Shape` with `radius` validated the same way
