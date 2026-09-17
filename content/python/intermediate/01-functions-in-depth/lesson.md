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

```python
def average(*values):
    return sum(values) / len(values)

average(1, 2, 3)        # values == (1, 2, 3), a tuple
```

## **kwargs: any number of keyword arguments

```python
def configure(**options):
    for key, value in options.items():
        print(key, "=", value)

configure(debug=True, level=3)    # options == {'debug': True, 'level': 3}
```

The names `args` and `kwargs` are only convention; the `*` and `**` do the work.

## Keyword-only parameters

Parameters after `*args`, or after a bare `*`, can **only** be passed by name.
Use this for flags and options that would be unreadable as positional values:

```python
def connect(host, port, *, timeout=10, retries=3):
    ...

connect("db", 5432, timeout=2)     # fine
connect("db", 5432, 2)             # TypeError: takes 2 positional arguments
```

There is also `/` for positional-only: `def f(a, b, /, c)`.

The full order is: positional-only, `/`, normal, `*args` or `*`, keyword-only, `**kwargs`.

## Unpacking into a call

The same symbols work the other way round:

```python
point = (3, 4)
distance(*point)                   # distance(3, 4)

settings = {"timeout": 2, "retries": 5}
connect("db", 5432, **settings)    # connect("db", 5432, timeout=2, retries=5)
```

## Functions are values

A function is an object like any other. You can store it, pass it, return it:

```python
def shout(s): return s.upper()
def whisper(s): return s.lower()

styles = {"loud": shout, "quiet": whisper}
styles["loud"]("hi")      # 'HI'
```

`lambda` makes a small anonymous function from a single expression. Its most
common use is a `key` for sorting:

```python
words = ["banana", "Apple", "cherry"]
sorted(words, key=str.lower)
sorted(words, key=lambda w: (len(w), w))   # by length, then alphabetically
```

Sorting by a tuple compares the first items, then the second on a tie. To
reverse just one part of a numeric key, negate it.

## The mutable default trap

Defaults are evaluated **once**, when the function is defined:

```python
def add_item(item, bucket=[]):     # the same list every call!
    bucket.append(item)
    return bucket

add_item(1)   # [1]
add_item(2)   # [1, 2]  surprise
```

Use `None` and create the list inside: `if bucket is None: bucket = []`.

## Your turn

In `functions.py`:

- `total(*numbers, start=0)`: `start` plus the sum of all numbers
- `describe(name, **attributes)`: `"cat (age=3, color=grey)"` with attributes
  sorted by name, or just `"cat"` if there are none
- `make_tag(tag, text, *, cls=None, id=None)`: `'<p class="note" id="x">hi</p>'`.
  Leave out attributes that are `None`; class comes before id. `cls` and `id`
  must be keyword-only.
- `apply_all(funcs, value)`: a list with each function applied to `value`
- `sort_people(people)`: `(name, age)` tuples sorted oldest first, and by name
  for equal ages
