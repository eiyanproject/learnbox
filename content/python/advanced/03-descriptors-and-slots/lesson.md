---
title: Descriptors and __slots__
summary: The mechanism behind properties and methods, reusable validated fields with __set_name__, and slimmer objects with __slots__.
order: 3
files: [fields.py]
run: python -i fields.py
hints:
  - "`__set_name__(self, owner, name)` stores `self.name = name` and a private storage name such as `\"_\" + name`."
  - "`__get__(self, obj, objtype=None)`: `if obj is None: return self` (accessed on the class), else `return getattr(obj, self.storage)`."
  - "`__set__` calls `self.validate(value)` then `setattr(obj, self.storage, value)`. Subclasses only override `validate`."
  - "`Product` uses `__slots__ = (\"_name\", \"_price\", \"_quantity\")`: the descriptors store into those slots, so no `__dict__` is needed."
---

## What a descriptor is

A **descriptor** is an object, stored as a **class** attribute, that defines
any of `__get__`, `__set__` or `__delete__`. When you access that attribute
through an instance, Python calls those methods instead of returning the object.

You have used descriptors all along: `property` is one, and every function in a
class is one too. That is how `obj.method` becomes a bound method with `self`
filled in.

```python
class Loud:
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self                 # accessed on the class: Thing.word
        return obj._word.upper()

    def __set__(self, obj, value):
        obj._word = value

class Thing:
    word = Loud()

t = Thing()
t.word = "hi"      # Loud.__set__(t, "hi")
t.word             # Loud.__get__(t, Thing) -> 'HI'
```

## __set_name__

Since Python 3.6, a descriptor learns the attribute name it was assigned to,
so the same descriptor class can back many fields:

```python
class Field:
    def __set_name__(self, owner, name):
        self.name = name
        self.storage = f"_{name}"
```

## Reusable validation

A property handles one attribute. A descriptor class handles a **kind** of
attribute, everywhere:

```python
class Positive(Field):
    def validate(self, value):
        if value <= 0:
            raise ValueError(f"{self.name} must be positive")

class Order:
    quantity = Positive()
    price = Positive()
```

This is exactly how ORMs (`Column(Integer)`) and form libraries define fields.

## Data and non-data descriptors

A descriptor with `__set__` (or `__delete__`) is a **data descriptor** and wins
over the instance `__dict__`. One with only `__get__` is a **non-data
descriptor**; an instance attribute of the same name hides it. That is why you
can shadow a method by assigning to `obj.method`, but not a property.

## __slots__

Normally every instance has a `__dict__`, which costs memory. Listing the
attributes in `__slots__` replaces it with fixed storage:

```python
class Point:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x, self.y = x, y

p = Point(1, 2)
p.z = 3          # AttributeError: no __dict__ to put it in
```

Slotted instances are smaller and attribute access is slightly faster. Use them
for classes with very many instances. Slots are themselves implemented as
descriptors on the class.

### Slots and descriptors together

Because a slot *is* a class attribute, a slot cannot share its name with
anything else defined on the class - including one of your descriptors:

```python
class Product:
    __slots__ = ("name",)
    name = String(40)        # ValueError: 'name' in __slots__ conflicts
                             # with class variable
```

That fails when the class is **defined**, before any of your code runs. The fix
is the one the exercise uses: the descriptor keeps the public name, and the
slot holds the private storage name it writes to.

```python
class Product:
    __slots__ = ("_name",)   # where the value lives
    name = String(40)        # the descriptor, writing into _name
```

## Your turn

In `fields.py`:

- `Field`: a base descriptor. `__set_name__` records the name and a storage
  name `_<name>`; `__get__` returns the descriptor itself on the class, and the
  stored value on instances; `__set__` calls `self.validate(value)` then stores.
  `validate` does nothing by default.
- `String(max_length)`: must be a `str` (else `TypeError`) no longer than
  `max_length` (else `ValueError`)
- `Positive`: must be an `int` or `float` (not `bool`, else `TypeError`) and `> 0`
- `NonNegativeInt`: must be an `int` (not `bool`) and `>= 0`
- `Product(name, price, quantity)`: `name = String(40)`, `price = Positive()`,
  `quantity = NonNegativeInt()`, uses `__slots__` so no other attributes can be
  added, and has `total()` returning `price * quantity`. Error messages include the field name.
