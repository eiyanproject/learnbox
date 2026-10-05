---
title: Functions in depth
summary: "*args, **kwargs, keyword-only parameters, unpacking, and functions as values."
order: 1
files: [functions.py]
run: python -i functions.py
hints:
  - "`def total(*numbers, start=0)`: `numbers` is a tuple, so `start + sum(numbers)` works."
  - "`describe`: `if not attributes: return name`, otherwise join `f\"{k}={v}\"` for `k` in `sorted(attributes)`."
  - "A bare `*` in the parameter list makes everything after it keyword-only: `def make_tag(tag, text, *, cls=None, id=None)`."
  - "`sort_people`: `sorted(people, key=lambda p: (-p[1], p[0]))`: negate the age to sort it descending while names stay ascending."
---

You already know `def`, defaults and return values. Python's parameter list
can do a lot more, and the standard library uses all of it.

## *args: any number of positional arguments

```pycon
>>> def average(*values):
...     return sum(values) / len(values)
...
>>> average(1, 2, 3)        # inside, values == (1, 2, 3), a tuple
2.0
```

## **kwargs: any number of keyword arguments

```python
def configure(**options):
    for key, value in options.items():
        print(key, "=", value)

configure(debug=True, level=3)    # options == {'debug': True, 'level': 3}
```

```output
debug = True
level = 3
```

The names `args` and `kwargs` are only convention; the `*` and `**` do the work.

## Keyword-only parameters

Parameters after `*args`, or after a bare `*`, can **only** be passed by name.
Use this for flags and options that would be unreadable as positional values:

```pycon
>>> def connect(host, port, *, timeout=10, retries=3):
...     return f"{host}:{port} timeout={timeout} retries={retries}"
...
>>> connect("db", 5432, timeout=2)     # fine
'db:5432 timeout=2 retries=3'
>>> connect("db", 5432, 2)
Traceback (most recent call last):
  ...
TypeError: connect() takes 2 positional arguments but 3 were given
```

There is also `/` for positional-only: `def f(a, b, /, c)`.

The full order is: positional-only, `/`, normal, `*args` or `*`, keyword-only, `**kwargs`.

## Unpacking into a call

The same symbols work the other way round:

```pycon
>>> def distance(x, y):
...     return (x * x + y * y) ** 0.5
...
>>> point = (3, 4)
>>> distance(*point)                   # distance(3, 4)
5.0
>>> settings = {"timeout": 2, "retries": 5}
>>> connect("db", 5432, **settings)    # connect("db", 5432, timeout=2, retries=5)
'db:5432 timeout=2 retries=5'
```

## Functions are values

A function is an object like any other. You can store it, pass it, return it:

```pycon
>>> def shout(s): return s.upper()
...
>>> def whisper(s): return s.lower()
...
>>> styles = {"loud": shout, "quiet": whisper}
>>> styles["loud"]("hi")
'HI'
```

`lambda` makes a small anonymous function from a single expression. Its most
common use is a `key` for sorting:

```pycon
>>> words = ["banana", "Apple", "cherry", "fig"]
>>> sorted(words)                            # capitals sort before lowercase
['Apple', 'banana', 'cherry', 'fig']
>>> sorted(["banana", "apple", "Cherry"], key=str.lower)
['apple', 'banana', 'Cherry']
>>> sorted(words, key=lambda w: (len(w), w))   # by length, then alphabetically
['fig', 'Apple', 'banana', 'cherry']
```

Sorting by a tuple compares the first items, then the second on a tie. To
reverse just one part of a numeric key, negate it.

## The mutable default trap

Defaults are evaluated **once**, when the function is defined:

```pycon
>>> def add_item(item, bucket=[]):     # the same list every call!
...     bucket.append(item)
...     return bucket
...
>>> add_item(1)
[1]
>>> add_item(2)     # surprise
[1, 2]
```

Use `None` and create the list inside: `if bucket is None: bucket = []`.

## Your turn

In `functions.py`:

- `total(*numbers, start=0)`: `start` plus the sum of all the numbers:
  `total(1, 2, 3)` is `6`, `total(1, 2, start=10)` is `13`, and `total()` is `0`
- `describe(name, **attributes)`: the name, then the attributes in brackets
  as `key=value`, sorted by key: `describe("cat", color="grey", age=3)` is
  `"cat (age=3, color=grey)"`. With no attributes it is just `"cat"`.
- `make_tag(tag, text, *, cls=None, id=None)`: an HTML element as a string.
  `make_tag("p", "hi")` is `'<p>hi</p>'`, and
  `make_tag("p", "hi", cls="note", id="x")` is
  `'<p class="note" id="x">hi</p>'`. An attribute that is `None` is left out,
  and `class` always comes before `id`. `cls` and `id` must be keyword-only.
- `apply_all(funcs, value)`: call every function in the list with `value` and
  return the results as a list: `apply_all([abs, str], -3)` is `[3, "-3"]`
- `sort_people(people)`: `people` is a list of `(name, age)` tuples. Return
  them oldest first; people of the same age go in name order.
  `[("Bo", 30), ("Ana", 41), ("Al", 30)]` gives
  `[("Ana", 41), ("Al", 30), ("Bo", 30)]`.
