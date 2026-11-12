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

In the first lesson of this section, a property validated one attribute.
But suppose ten classes each have several prices that must be positive.
Writing a property, getter and setter, for every one of them is a lot of
copied code. A **descriptor** lets you write that validation once, as a
class, and reuse it for every such attribute. Descriptors are also the
machinery behind properties, methods and `__slots__`, so understanding them
explains a good deal of how Python's objects work.

## What a descriptor is

A **descriptor** is an object, stored as a **class** attribute, that defines
any of the methods `__get__`, `__set__` or `__delete__`. When you access that
attribute through an instance, Python does not hand you the descriptor
object. It calls those methods instead, and you get whatever they return:

- reading `obj.attr` calls `__get__(self, obj, objtype)`, where `self` is the
  descriptor, `obj` the instance, and `objtype` the instance's class;
- assigning `obj.attr = value` calls `__set__(self, obj, value)`;
- `del obj.attr` calls `__delete__(self, obj)`.

You have used descriptors all along: `property` is one, and every function
defined in a class is one too. That is how `obj.method` becomes a bound
method with `self` filled in: a function's `__get__` returns a new object
that remembers which instance it came from.

```pycon
>>> class Loud:
...     def __get__(self, obj, objtype=None):
...         if obj is None:
...             return self                 # accessed on the class: Thing.word
...         return obj._word.upper()
...
...     def __set__(self, obj, value):
...         obj._word = value
...
>>> class Thing:
...     word = Loud()
...
>>> t = Thing()
>>> t.word = "hi"      # Loud.__set__(t, "hi")
>>> t.word             # Loud.__get__(t, Thing)
'HI'
>>> t.__dict__         # the stored value is the one __set__ wrote
{'_word': 'hi'}
```

Step by step:

1. `word = Loud()` puts one `Loud` object on the class `Thing`. It is shared
   by every `Thing`; it does not store any values itself.
2. `t.word = "hi"` finds that `word` on the class is a descriptor with
   `__set__`, so instead of storing `"hi"` under `word`, it calls
   `Loud.__set__(descriptor, t, "hi")`. That stores the value on the instance
   under a different name, `_word`.
3. `t.word` calls `Loud.__get__(descriptor, t, Thing)`, which reads `_word`
   from the instance and returns it upper-cased.
4. `t.__dict__` holds an instance's own attributes. It has `_word`, not
   `word`: the descriptor decided where the data lives.

The `if obj is None` check handles access through the class, `Thing.word`,
where there is no instance. Returning the descriptor itself there is the
convention, and it lets you inspect the descriptor:

```pycon
>>> Thing.word
<__main__.Loud object at 0x...>
```

## __set_name__

A descriptor object has a problem: it is created by `Loud()` before it is
assigned to a name, so it does not know which attribute it is. Since
Python 3.6, Python solves this by calling `__set_name__(self, owner, name)` on
each descriptor when the class is created, with the class (`owner`) and the
attribute name it was assigned to. So the same descriptor class can back
many fields, each storing under its own name:

```python
class Field:
    def __set_name__(self, owner, name):
        self.name = name
        self.storage = f"_{name}"
```

(This is only the naming part of a `Field`; the full one, with `__get__` and
`__set__`, is this lesson's exercise.)

```pycon
>>> class Named:
...     def __set_name__(self, owner, name):
...         self.name = name
...
>>> class Order:
...     price = Named()
...     quantity = Named()
...
>>> Order.__dict__["price"].name, Order.__dict__["quantity"].name
('price', 'quantity')
```

(`Order.__dict__["price"]` reaches the descriptor object directly, without
going through `__get__`.)

## Reusable validation

A property handles one attribute. A descriptor class handles a **kind** of
attribute, everywhere. Put the storing logic in a base class once, and each
subclass only says what counts as valid (a fragment, built on the full
`Field` from the exercise):

```python
class Positive(Field):
    def validate(self, value):
        if value <= 0:
            raise ValueError(f"{self.name} must be positive")

class Order:
    quantity = Positive()
    price = Positive()
```

`Order` now validates both attributes with two short lines, and any other
class can reuse `Positive` the same way. Because `__set_name__` gave each
descriptor its name, the error message says *which* field was wrong:
`price must be positive`.

This is exactly how ORMs (libraries that map classes to database tables,
with fields like `Column(Integer)`) and form libraries define their fields.

## Data and non-data descriptors

Python looks for an attribute in two places: the instance's own `__dict__`,
and the class. Descriptors come in two kinds, and the kind decides which
place wins:

- A descriptor with `__set__` (or `__delete__`) is a **data descriptor**. It
  wins over the instance `__dict__`: even if the instance has an entry of
  the same name, the descriptor's `__get__` runs.
- One with only `__get__` is a **non-data descriptor**. An instance attribute
  of the same name hides it.

Functions are non-data descriptors, and `property` is a data descriptor.
That is why you can shadow a method on one object by assigning to
`obj.method`, but assigning to a property always goes through its setter (or
fails, if it has none):

```pycon
>>> class Demo:
...     def hello(self):
...         return "method"
...     @property
...     def size(self):
...         return 1
...
>>> d = Demo()
>>> d.hello = lambda: "replaced"    # the instance attribute hides the method
>>> d.hello()
'replaced'
>>> d.size = 5                      # a property with no setter refuses
Traceback (most recent call last):
  ...
AttributeError: property 'size' of 'Demo' object has no setter
```

## __slots__

Normally every instance carries its own `__dict__`, a full dictionary, so
that any attribute can be added to it at any time. That flexibility costs
memory, which adds up across millions of small objects. Listing the allowed
attributes in a class attribute called `__slots__` replaces the dict with
fixed storage for exactly those names:

```pycon
>>> class Point:
...     __slots__ = ("x", "y")
...     def __init__(self, x, y):
...         self.x, self.y = x, y
...
>>> p = Point(1, 2)
>>> p.x
1
>>> p.z = 3          # no __dict__ to put it in
Traceback (most recent call last):
  ...
AttributeError: 'Point' object has no attribute 'z'...
>>> hasattr(p, "__dict__")
False
```

Slotted instances are smaller and attribute access is slightly faster. The
price is flexibility: no attributes beyond the listed ones. Use them for
classes with very many instances, or when a fixed set of attributes is a
feature in itself (a typo like `p.xx = 1` becomes an error instead of
silently creating a new attribute). Slots are themselves implemented as
descriptors on the class, one per name.

### Slots and descriptors together

Because a slot *is* a class attribute (a descriptor named after the slot), a
slot cannot share its name with anything else defined on the class -
including one of your descriptors:

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

`p.name = "tea"` then runs `String.__set__`, which validates and stores into
the slot `_name`, and no `__dict__` is ever needed.

## Your turn

In `fields.py`:

- `Field`: a base descriptor. `__set_name__` records the name and a storage
  name `_<name>`; `__get__` returns the descriptor itself on the class, and the
  stored value on instances; `__set__` calls `self.validate(value)` then stores.
  `validate` does nothing by default. The same descriptor class must work for
  several attributes of one class independently.
- `String(max_length)`: the value must be a `str` (else `TypeError`) no longer
  than `max_length` characters (else `ValueError`). Exactly `max_length` is
  allowed.
- `Positive`: the value must be an `int` or `float` (else `TypeError`) and
  `> 0` (else `ValueError`). `True` and `False` are technically `int`s in
  Python (`isinstance(True, int)` is `True`), so reject `bool` explicitly
  with `TypeError`.
- `NonNegativeInt`: must be an `int`, again not a `bool` (else `TypeError`;
  a float such as `2.5` is a `TypeError` too), and `>= 0` (else
  `ValueError`).
- `Product(name, price, quantity)`: `name = String(40)`, `price = Positive()`,
  `quantity = NonNegativeInt()`, uses `__slots__` so no other attributes can be
  added (and instances have no `__dict__`), and has `total()` returning
  `price * quantity`. Every `ValueError` message must include the field's
  name, such as `"price must be positive"`. A rejected value must leave the
  old one in place.
