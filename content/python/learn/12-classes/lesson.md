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

Every value in Python is an **object**: a bundle of data together with the
operations that make sense for that data. A list holds its items and knows how
to `append`, `sort` and `pop` them; a string holds its characters and knows how
to `upper` and `split` them. A **class** is the blueprint that says what data
an object of that kind holds and what it can do. Each object made from a
class is called an **instance** of it.

You have used many classes already: `str`, `list` and `dict` are classes,
`"hi"` is an instance of `str`, and `"hi".upper()` calls a method on that
`str` object. In this lesson you write classes of your own, so that your
programs can have types like `Rectangle` or `Account` that bundle their data
with the functions that work on it.

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
print(box.area())
box.scale(2)
print(box.width)
```

```output
12
6
```

Piece by piece:

- `class Rectangle:` starts the class. Class names are written with a
  capital letter for each word (`Rectangle`, `BankAccount`), which tells
  readers at a glance that the name is a class. Everything indented under it
  belongs to the class.
- The functions defined inside a class are its **methods**.
- `__init__` (two underscores on each side, read "dunder init") sets up a
  new object. You never call it by name: writing `Rectangle(3, 4)` creates a
  fresh, empty object and Python calls `__init__` on it for you, passing the
  `3` and `4` along. Its job is to store the starting data. It returns
  nothing; the call `Rectangle(3, 4)` itself gives you the new object.
- `self` is the object the method was called on. It is always the first
  parameter, and Python fills it in: `box.area()` is really
  `Rectangle.area(box)`, so inside `area`, `self` is `box`. You leave `self`
  out when you call a method, but you must list it first when you define one.
  (`self` is only a convention, but every Python programmer uses it.)
- `self.width = ...` creates an **attribute**: a variable stored on that
  particular object. Attributes are read and set with a dot, from inside the
  class (`self.width`) or from outside it (`box.width`).

`scale` shows that a method can change the object it belongs to: after
`box.scale(2)`, `box.width` is 6. It returns nothing, because the change
itself is the point.

## Each object has its own data

Each instance has its own attributes. Changing one object does not affect
another, even though both were made from the same class:

```python
a = Rectangle(1, 1)
b = Rectangle(5, 5)
a.scale(10)
print(a.width, b.width)   # 10 5
```

`self` is what makes this work. When you call `a.scale(10)`, `self` is `a`,
so only `a`'s attributes change.

## Printing and comparing: dunder methods

Methods whose names start and end with double underscores, like `__init__`,
are called **dunder methods** (or special methods). You do not call them
yourself; Python calls them when your object is used with built-in
operations. Defining one lets your class decide how that operation behaves:

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):              # what print() and the >>> prompt show
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other):         # what == does
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)
```

With those two methods defined, a `Point` behaves like a built-in value:

```python
p = Point(1, 2)
print(p)                  # Point(1, 2)
print(p == Point(1, 2))   # True
print(p == Point(2, 1))   # False
print(p == "Point(1, 2)") # False: a string is not a Point
```

Without `__repr__` you get something like `<__main__.Point object at
0x7f...>`: the class name and a memory address, which tells you nothing
useful. The convention is for `__repr__` to return text that looks like the
code that would create the object, as here. It must *return* a string, not
print one.

Without `__eq__`, `==` is only true when both sides are the very same object,
so two separate points with equal coordinates would not be equal. The
`__eq__` here first checks `isinstance(other, Point)`, "is the other value a
`Point` at all?", so that comparing a point with something unrelated, like a
string, gives `False` instead of crashing when it tries to read `other.x`. It
then compares the coordinates as a tuple, which checks them all in one go.

Inside an f-string, `!r` after a value uses its `repr()` instead of its
normal text. For a string that adds the quotes: `f"{'Ana'!r}"` gives `'Ana'`
with the quote marks, which is how `Account('Ana', 5)` gets its quotes in this
lesson's exercise.

## Class attributes

A variable assigned in the class body itself, outside any method, belongs to
the class rather than to any one object, and is shared by all of them:

```pycon
>>> class Account:
...     interest_rate = 0.02
...
>>> a, b = Account(), Account()
>>> a.interest_rate, b.interest_rate
(0.02, 0.02)
>>> Account.interest_rate = 0.03     # change it on the class...
>>> a.interest_rate, b.interest_rate # ...and every object sees it
(0.03, 0.03)
```

When you read `a.interest_rate`, Python looks on the object first and, if
the object has no attribute of that name, on its class. Use class attributes
for values that really are the same for every object, such as a rate or a
limit. Data that differs per object belongs on `self`, set in `__init__`.

## Inheritance, briefly

A class can be based on another class, written in brackets after its name.
The new class, the **subclass**, **inherits** every method of the original,
the **base class**, and only needs to define what is different. A method it
defines with the same name as one in the base class **overrides** it, that
is, replaces it for the subclass:

```python
class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)


sq = Square(3)
print(sq.width, sq.height)    # 3 3
print(sq.area())              # 9
```

A square is a rectangle whose sides are equal, so `Square` only changes how
the object is set up: it takes a single `side`. `super()` gives you the base
class's version of a method, so `super().__init__(side, side)` runs
`Rectangle`'s `__init__` with the side as both width and height, and that
stores `self.width` and `self.height` exactly as before.

`Square(3).area()` works, and gives 9, because `area` comes from `Rectangle`.
`Square` never had to write it. This is the same mechanism you used in the
last lesson: `class OutOfStock(Exception)` made a subclass of `Exception`.

## dataclasses

Many classes mostly hold data, and writing `__init__`, `__repr__` and
`__eq__` for each of them is repetitive. The `@dataclass` line placed above a
class, called a **decorator**, writes those three methods for you from a list
of the fields and their types:

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int


p = Point(1, 2)
print(p)                  # Point(x=1, y=2)
print(p == Point(1, 2))   # True
```

`x: int` means "a field called `x`, which should hold an `int`". Those two
lines are all it takes: `Point(1, 2)` works, prints as `Point(x=1, y=2)` and
compares with `==` by its fields. (Python does not check the types; they are notes for
readers and tools. Dataclasses and type hints both come back in the
Intermediate section.)

Writing the methods by hand once, as this exercise asks, is the best way to
see what it saves you.

## Your turn

In `classes.py`, finish the `Account` class:

- `Account("Ana")` starts with balance `0`; `Account("Ana", 100)` with `100`.
  `history` starts as an empty list. Store them as the attributes `owner`,
  `balance` and `history`.
- `deposit(amount)` adds to the balance and appends the tuple
  `("deposit", amount)` to `history`.
- `withdraw(amount)` subtracts from the balance and appends
  `("withdraw", amount)`. If the amount is more than the balance, raise
  `ValueError` without changing anything: check first, before you touch
  `balance` or `history`.
- Both raise `ValueError` for amounts that are zero or negative.
- `transfer_to(other, amount)` moves money from this account to another
  `Account`, `other`. If it fails, neither account changes. Reusing your own
  `withdraw` and `deposit` methods (as `self.withdraw(...)` and
  `other.deposit(...)`) means the checks and the history come for free.
- `repr(Account("Ana", 5))` is `"Account('Ana', 5)"`.
- Two accounts are `==` when owner and balance are both equal (their
  histories do not matter).
