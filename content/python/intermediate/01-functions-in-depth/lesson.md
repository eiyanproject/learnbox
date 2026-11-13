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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **parameter list** | the names in brackets after a function's name in `def` |
| **signature** | a function's name with its parameter list, as the documentation shows it |
| **standard library** | the modules that come with Python |
| **positional argument** | an argument matched to a parameter by its position |
| **keyword argument** | an argument passed as `name=value` |
| **`*args`** | a parameter that collects all remaining positional arguments into a tuple |
| **`**kwargs`** | a parameter that collects all remaining keyword arguments into a dict |
| **keyword-only parameter** | one after `*args` or a bare `*`; it can only be passed by name |
| **positional-only parameter** | one before a `/`; it can never be passed by name |
| **flag** | an option that switches behaviour on or off, best passed by name |
| **unpacking into a call** | `*` spreads a list or tuple out as positional arguments; `**` a dict as keyword arguments |
| **function as a value** | a function name without brackets is the function itself, which can be stored or passed |
| **higher-order function** | a function that takes or returns other functions: `sorted(..., key=len)` |
| **lambda** | a small nameless function made from one expression: `lambda w: len(w)` |
| **sort key** | the value `sorted` compares for each item instead of the item |
| **character code** | the number of each character; every capital letter comes before every lowercase one |
| **tuple comparison** | item by item: the second items are compared only if the first are equal |
| **negating a key** | `-p[1]` sorts that part largest first while other parts stay in normal order |
| **mutable default trap** | a default list (or dict, set) is made once when `def` runs, and shared by every call |
| **identity** (`is`) | "the very same object", not "equal" |
| **HTML element** | a piece of a web page: `<p class="note">hi</p>` |

### Python syntax and functions

| Name | What it does |
|---|---|
| `def f(*values):` | `values` is a tuple of every positional argument |
| `def f(**options):` | `options` is a dict of every extra keyword argument |
| `def f(a, *, flag=False):` | a bare `*`: everything after it is keyword-only |
| `def f(a, b, /, c):` | a `/`: everything before it is positional-only |
| `f(*point)`, `f(**settings)` | spread a sequence or a dict into the call |
| `options.items()` | the key-value pairs of a dict |
| `sum(values) / len(values)` | the average |
| `lambda params: expression` | a one-expression function; no `return` keyword |
| `sorted(words, key=str.lower)` | sort ignoring case; `str.lower` is the `lower` method taken from the class |
| `sorted(..., reverse=True)` | largest first, for every part of the key at once |
| `x is None` | the usual test for `None` |
| `abs(x)` | the number without its sign: `abs(-3)` is `3` |
| `str(x)` | as text |
| `print(*objects, sep=' ', end='\n')` | `print`'s own signature: any number of values, then keyword-only options |

### Errors

| Error | Means |
|---|---|
| `TypeError` | the call does not fit the parameters, such as a third positional argument to a function that takes two |
| `ZeroDivisionError` | averaging an empty tuple |

---

You already know `def`, defaults and return values. Python's parameter list
can do a lot more, and the standard library uses all of it: once you know
the pieces in this lesson, signatures like `print(*objects, sep=' ', end='\n')`
in the documentation stop looking like line noise.

## *args: any number of positional arguments

A normal parameter list fixes how many arguments a function takes. A
parameter written with one `*` in front collects **all** the remaining
positional arguments, however many there are, into a tuple:

```pycon
>>> def average(*values):
...     return sum(values) / len(values)
...
>>> average(1, 2, 3)        # inside, values == (1, 2, 3), a tuple
2.0
>>> average(10)             # one argument is fine too: (10,)
10.0
```

With no arguments at all, `values` would be the empty tuple `()`, and this
particular function would divide by zero, so a real version would check for
that first. That is the price of accepting "any number": zero is a number.

## **kwargs: any number of keyword arguments

Two stars do the same for keyword arguments. Every `name=value` argument
that does not match another parameter is collected into a dict, with the
names as string keys:

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

You will see these written as `*args` and `**kwargs` (short for "keyword
arguments") in a great deal of Python code. The names `args` and `kwargs` are
only a convention; the `*` and `**` do the work, so `*values` and `**options`
are equally valid and often clearer.

A function can have both, alongside ordinary parameters. Ordinary parameters
are filled first, and the starred ones collect whatever is left over:

```pycon
>>> def show(first, *rest, **named):
...     return first, rest, named
...
>>> show(1, 2, 3, colour="red")
(1, (2, 3), {'colour': 'red'})
```

## Keyword-only parameters

Parameters after `*args`, or after a bare `*`, can **only** be passed by name.
The reason is simple: everything positional has already been swallowed by
the `*`, so there is no position left for them. A bare `*` on its own does
the same without collecting any extra arguments; it only marks "everything
after this must be named".

Use this for flags and options that would be unreadable as positional
values. Compare `connect("db", 5432, 2, 5)` with
`connect("db", 5432, timeout=2, retries=5)`: in the first, nobody can tell
what 2 and 5 mean without looking up the function.

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

The error message says "takes 2 positional arguments" because `host` and
`port` are the only parameters that can be filled by position; the `2` had
nowhere to go.

There is also the opposite: a `/` in the parameter list makes everything
**before** it positional-only, so those arguments can never be passed by
name. In `def f(a, b, /, c)`, `f(1, 2, 3)` and `f(1, 2, c=3)` work, but
`f(a=1, b=2, c=3)` is an error. It is used when the parameter names are not
meant to be part of how the function is called, which leaves the author free
to rename them later. Many built-ins work this way: `len(obj=[1])` is an
error.

The full order, when a function uses everything, is:

1. positional-only parameters, then `/`
2. normal parameters (by position or by name)
3. `*args`, or a bare `*`
4. keyword-only parameters
5. `**kwargs`

For example: `def report(source, /, title, *pages, draft=False, **meta)`.
Few real functions need all five; most use one or two of these features.

## Unpacking into a call

The same symbols work the other way round, in a **call** rather than a
definition. `*` in front of a list or tuple spreads its items out as separate
positional arguments, and `**` in front of a dict spreads it out as keyword
arguments, one per key:

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

A function is an object like any other. You can store it in a variable, put
it in a list or dict, pass it to another function, or return it from one.

The key is the brackets. `shout` on its own is the function itself, the
thing; `shout("hi")` *calls* it and gives you what it returns. Leave the
brackets off and you are handling the function without running it:

```pycon
>>> def shout(s): return s.upper()
...
>>> def whisper(s): return s.lower()
...
>>> styles = {"loud": shout, "quiet": whisper}
>>> styles["loud"]("hi")
'HI'
```

`styles["loud"]` looks up the function stored under `"loud"`, and the
`("hi")` after it calls that function. A dict of functions like this is a
neat replacement for a long `if`/`elif` chain that picks what to do.

(Putting a short body on the same line as `def`, as above, is legal and saves
space in examples, but in real code the body usually goes on its own line.)

A function that takes or returns other functions is called a
**higher-order function**. `sorted(..., key=len)` is one: you hand it `len`,
and it calls `len` on every item to decide the order.

`lambda` makes a small function without a name, from a single expression.
`lambda w: len(w)` means the same as:

```python
def some_name(w):
    return len(w)
```

The parameters go between `lambda` and the colon, and the expression after
the colon is what it returns; there is no `return` keyword, and the body can
only be one expression. Its most common use is as a throwaway `key` for
sorting, where writing a whole `def` would be overkill:

```pycon
>>> words = ["banana", "Apple", "cherry", "fig"]
>>> sorted(words)                            # capitals sort before lowercase
['Apple', 'banana', 'cherry', 'fig']
>>> sorted(["banana", "apple", "Cherry"], key=str.lower)
['apple', 'banana', 'Cherry']
>>> sorted(words, key=lambda w: (len(w), w))   # by length, then alphabetically
['fig', 'Apple', 'banana', 'cherry']
```

Three things are going on here:

- Strings sort by the code number of each character, and in that numbering
  every capital letter comes before every lowercase letter. So `"Apple"`
  sorts before `"banana"`, and `"Zebra"` would too.
- `key=str.lower` makes the sort compare lower-cased copies, so case is
  ignored. The original strings are what come back, with their capitals
  intact. `str.lower` is the `lower` method taken from the `str` class
  itself, which is a function that takes a string.
- `key=lambda w: (len(w), w)` gives each word a tuple to be sorted by.
  Tuples compare item by item: the first items are compared, and only if
  they are equal are the second items compared, and so on. So the words are
  sorted by length, and words of the same length, here `"banana"` and
  `"cherry"`, fall back to alphabetical order.

To reverse only one part of a numeric key, negate it. `key=lambda p: (-p[1],
p[0])` sorts by `p[1]` from largest to smallest (because -41 is smaller than
-30, so it comes first), while ties on that are still broken by `p[0]` in
normal order. `reverse=True` cannot do this, because it flips every part of
the key at once.

## The mutable default trap

A default value is worked out **once**, when the `def` line runs, not each
time the function is called. Every call that leaves the argument out gets
that same object. For a number or a string this never matters, since those
cannot change. For a list it matters a lot, because the function can change
it, and the change is still there the next time:

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

The second call did not get a new empty list. It got the same list the first
call had already appended to.

The standard fix is to use `None` as the default and create the list inside
the function, where that line runs fresh on every call:

```pycon
>>> def add_item(item, bucket=None):
...     if bucket is None:
...         bucket = []
...     bucket.append(item)
...     return bucket
...
>>> add_item(1)
[1]
>>> add_item(2)
[2]
```

`is None` is the usual way to test for `None`. `is` asks "is this the very
same object?" rather than "is this equal?", and there is only one `None`.
The same trap applies to a default dict or set: use `None` for those as well.

## Your turn

In `functions.py`:

- `total(*numbers, start=0)`: `start` plus the sum of all the numbers:
  `total(1, 2, 3)` is `6`, `total(1, 2, start=10)` is `13`, and `total()` is `0`
- `describe(name, **attributes)`: the name, then the attributes in brackets
  as `key=value`, sorted by key and separated by a comma and a space:
  `describe("cat", color="grey", age=3)` is `"cat (age=3, color=grey)"`.
  With no attributes it is `"cat"` on its own, with no brackets.
- `make_tag(tag, text, *, cls=None, id=None)`: an HTML element as a string.
  `make_tag("p", "hi")` is `'<p>hi</p>'`, and
  `make_tag("p", "hi", cls="note", id="x")` is
  `'<p class="note" id="x">hi</p>'`. An attribute that is `None` is left out,
  and `class` always comes before `id`. `cls` and `id` must be keyword-only.
  (The parameter is called `cls` rather than `class` because `class` is a
  Python keyword and cannot be used as a name.)
- `apply_all(funcs, value)`: call every function in the list with `value` and
  return the results as a list: `apply_all([abs, str], -3)` is `[3, "-3"]`
- `sort_people(people)`: `people` is a list of `(name, age)` tuples. Return
  them oldest first; people of the same age go in name order.
  `[("Bo", 30), ("Ana", 41), ("Al", 30)]` gives
  `[("Ana", 41), ("Al", 30), ("Bo", 30)]`.
