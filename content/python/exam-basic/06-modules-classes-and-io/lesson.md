---
title: "Paper 6: modules, classes and I/O"
summary: import forms and __name__, class versus instance attributes, super() and isinstance, with-blocks and f-string formatting.
order: 6
files: [parts.py]
run: python -i parts.py
hints:
  - "A class attribute is shared by every instance. Increment it as `Shape.created += 1` inside `__init__` - writing `self.created += 1` would create a new *instance* attribute and leave the class one alone."
  - "`super().__init__(name)` calls the parent's `__init__`; without it the parent never runs and its attributes never exist."
  - "`with open(path, \"w\", encoding=\"utf-8\") as f:` closes the file even if the block raises. `f.write` does not add newlines - add them yourself."
  - "Format specs go after a colon: `f\"{name:<10}\"` left-aligns in 10 columns, `f\"{score:>6.1f}\"` right-aligns to one decimal in 6."
---

The last paper collects the four small sections — modules, classes, input and
output, and virtual environments — worth six questions between them.

## Modules

```python
import math              # math.pi
import math as m         # m.pi
from math import pi      # pi
from math import *       # everything - discouraged, it hides what came from where
```

Every module has a `__name__`. When you run a file directly it is `"__main__"`;
when the same file is imported it is the module's name. That is the entire
reason for the idiom:

```python
if __name__ == "__main__":
    main()
```

A **package** is a directory Python can import. A virtual environment is made
with `python -m venv .venv` and holds its own `site-packages`, which is why
`pip install` inside one does not touch the system Python.

## Classes

```python
class Shape:
    created = 0                    # class attribute - one, shared

    def __init__(self, name):
        self.name = name           # instance attribute - one per object
        Shape.created += 1
```

Reading `self.created` finds the class attribute; **assigning** `self.created`
creates a separate instance attribute that shadows it. That distinction is the
exam's favourite class question:

```pycon
>>> class Counter:
...     count = 0
...
>>> a, b = Counter(), Counter()
>>> a.count += 1            # reads the class's 0, then assigns 1 to a itself
>>> a.count, b.count, Counter.count
(1, 0, 0)
>>> Counter.count += 1      # changes the one shared value
>>> a.count, b.count, Counter.count
(1, 1, 1)
```

`a.count += 1` means `a.count = a.count + 1`. The right-hand side reads the
class attribute (0), but the assignment creates a new attribute on `a` alone.
From then on `a` has its own `count`, which hides the class's, and the class
value never changed. Updating through the class name, `Counter.count += 1`,
is the only way to change the shared value, and every instance without its
own `count` sees it.

```python
class Rect(Shape):
    def __init__(self, w, h):
        super().__init__("rect")   # without this, self.name never exists
        self.w, self.h = w, h
```

`isinstance(obj, Shape)` is True for a `Rect` as well — it walks the hierarchy.
`type(obj) is Shape` does not.

## Files and formatting

```python
with open(path, "w", encoding="utf-8") as f:
    f.write("line\n")
```

The `with` block closes the file even if the body raises. Modes: `"r"` read,
`"w"` truncate (empty the file, or create it, then write), `"a"` append,
`"x"` create, failing if it exists. `read()` gives the whole file,
`readlines()` a list of lines **with** their newlines, and
`read().splitlines()` a list of lines without them. `encoding="utf-8"` names
how the text is stored as bytes; without it, Python uses the system's
default, which differs between machines.

```pycon
>>> import os, tempfile
>>> path = os.path.join(tempfile.mkdtemp(), "demo.txt")
>>> with open(path, "w", encoding="utf-8") as f:
...     _ = f.write("one\ntwo\n")
...
>>> with open(path, encoding="utf-8") as f:
...     print(f.readlines())
...
['one\n', 'two\n']
>>> with open(path, encoding="utf-8") as f:
...     print(f.read().splitlines())
...
['one', 'two']
```

(`write` returns the number of characters written; `_ =` keeps the prompt
from showing it.)

Format specifications go after a colon inside an f-string's braces. `<`
aligns left and `>` aligns right, the number after it is the column width,
and `.1f` means one decimal place:

```pycon
>>> f"[{'ana':<6}]"
'[ana   ]'
>>> f"[{3.14159:>6.1f}]"
'[   3.1]'
>>> f"[{'verylongname':<6}]"     # too long: never cut, the column just grows
'[verylongname]'
```

Rounding to one decimal follows the same rule as `round()`: an exact half
goes to the even digit, so `9.25` (which is stored exactly in binary) shows
as `9.2`, and `8.75` as `8.8`.

## Your turn

In `parts.py`:

- `Shape`: its `__init__(name)` stores `name` on the instance and adds one to
  `Shape.created`, a class attribute that starts at `0` and so counts how
  many shapes have ever been made. Its `area()` raises `NotImplementedError`.
- `Rect(Shape)`: takes a width and a height, calls `super().__init__("rect")`
  so that it has a name and is counted, and has an `area()` that works:
  `Rect(2, 3).area()` is `6`.
- `save_lines(path, lines)` writes each item of the list as one line of the
  file, each followed by a newline (`["a", "b"]` gives the file `"a\nb\n"`),
  replacing anything the file held before. `load_lines(path)` reads them back
  as a list of strings with no newline characters on the ends; an empty file
  gives `[]`. What you load is what you saved. Use `encoding="utf-8"`.
- `render(name, score)`: one line of a results table as a string: `name`
  left-aligned in a column 10 characters wide, immediately followed by
  `score` right-aligned in a column 6 wide, to one decimal place.
  `render("ana", 9.25)` is `"ana          9.2"`. A name longer than 10
  characters is not cut; it pushes the score along.
