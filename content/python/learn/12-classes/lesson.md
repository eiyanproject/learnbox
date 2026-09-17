---
title: Classes
summary: Bundle data with the functions that work on it, and control how objects print and compare.
order: 12
files: [classes.py]
run: python -i classes.py
hints:
  - "`__init__(self, owner, balance=0)` stores the values: `self.owner = owner`, `self.balance = balance`, and an empty `self.history = []`."
  - "Methods change `self`: `self.balance += amount` and `self.history.append((\"deposit\", amount))`."
  - "`__repr__` must return a string, for example `f\"Account({self.owner!r}, {self.balance})\"`."
  - "`transfer_to(self, other, amount)`: call `self.withdraw(amount)` first, so an error leaves both accounts unchanged, then `other.deposit(amount)`."
---

A **class** is a blueprint for objects that carry their own data and
behaviour. You have used many already: `str`, `list` and `dict` are classes,
and `"hi".upper()` calls a method on a `str` object.

## Defining one

```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def scale(self, factor):
        self.width *= factor
        self.height *= factor


box = Rectangle(3, 4)    # calls __init__
box.area()               # 12
box.scale(2)
box.width                # 6
```

- `__init__` sets up a new object. Python calls it for you.
- `self` is the object the method was called on. It is always the first
  parameter, and Python fills it in: `box.area()` is really `Rectangle.area(box)`.
- `self.width = ...` creates an **attribute** stored on that particular object.

## Each object has its own data

```python
a = Rectangle(1, 1)
b = Rectangle(5, 5)
a.scale(10)
b.width      # still 5
```

## Printing and comparing: dunder methods

Methods with double underscores hook into Python's built-in behaviour:

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):              # what print() and the >>> prompt show
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other):         # what == does
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)
```

Without `__repr__` you get `<__main__.Point object at 0x7f...>`. Without
`__eq__`, `==` is only true for the very same object.

## Class attributes

A value defined in the class body is shared by all objects:

```python
class Account:
    interest_rate = 0.02
```

## Inheritance, briefly

A class can extend another and override what it needs:

```python
class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)
```

`Square(3).area()` works because `area` comes from `Rectangle`.

## dataclasses

For classes that mostly hold data, `@dataclass` writes `__init__`, `__repr__`
and `__eq__` for you:

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
```

Writing them by hand once, as below, is the best way to see what it saves you.

## Your turn

In `classes.py`, finish the `Account` class:

- `Account("Ana")` starts with balance `0`; `Account("Ana", 100)` with `100`.
  `history` starts as an empty list.
- `deposit(amount)` adds to the balance and appends `("deposit", amount)` to history
- `withdraw(amount)` subtracts and appends `("withdraw", amount)`. Raise
  `ValueError` without changing anything if the amount is more than the balance.
- Both raise `ValueError` for amounts that are zero or negative.
- `transfer_to(other, amount)` moves money to another account. If it fails,
  neither account changes.
- `repr(Account("Ana", 5))` is `"Account('Ana', 5)"`
- Two accounts are `==` when owner and balance are both equal.
