---
title: Modules and packages
summary: Split code across files, build a package with __init__.py, relative imports, and the __main__ guard.
order: 8
files: [shop/__init__.py, shop/pricing.py, shop/cart.py, main.py]
run: python main.py
hints:
  - "In `shop/cart.py`, import from a sibling module with a relative import: `from .pricing import apply_discount`."
  - "`shop/__init__.py` re-exports the public names: `from .cart import Cart` and `from .pricing import apply_discount, TAX_RATE`, then `__all__ = [\"Cart\", \"apply_discount\", \"TAX_RATE\"]`."
  - "`Cart.total()` sums `price * qty`, applies the discount with `apply_discount`, then adds tax: `round(subtotal * (1 + TAX_RATE), 2)`."
  - "`main.py` does its work inside `def main():` and ends with `if __name__ == \"__main__\": main()` so importing it prints nothing."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **module** | one `.py` file; its name is the file name without `.py` |
| **import** | load a module (running it once) and get access to its top-level names |
| **top level** | code in a file that is not inside a function or class |
| **alias** | another name for an imported module: `import statistics as stats` |
| **`sys.modules`** | the dict of every imported module; a second import reuses the entry |
| **`sys.path`** | the list of folders Python searches for modules, in order |
| **standard library** | the modules that come with Python |
| **third-party package** | code installed from elsewhere, such as `numpy` |
| **package** | a folder of modules containing `__init__.py`; modules inside are reached with a dot: `shop.cart` |
| **`__init__.py`** | runs when the package is first imported; the place to define its public names |
| **public surface** (interface) | the names other code is meant to use |
| **`__all__`** | the list of public names, and what `from package import *` brings in |
| **relative import** | importing by position in the package: `.` this package, `..` the one above |
| **script** | a file run directly as a program |
| **`__name__`** | a module's name; `"__main__"` for the file you ran directly |
| **`__main__` guard** | `if __name__ == "__main__": main()`, so importing the file does not run the program |
| **side effect** | work done just by importing, such as printing |
| **circular import** | two modules importing each other, so one is only half run |
| **constant** | a value that does not change, in capitals: `TAX_RATE` |
| **tax** / **discount** | a percentage added / a percentage taken off |

### Python statements and functions

| Name | What it does |
|---|---|
| `import math` | gives one name, `math`; everything is reached through it: `math.sqrt(16)` |
| `from math import pi` | copies one name into your file |
| `import statistics as stats` | imports under a shorter name |
| `from .pricing import apply_discount` | a relative import from the same package |
| `math.sqrt(x)`, `math.pi` | square root; the number pi |
| `statistics.mean(values)` | the average |
| `round(x, 2)` | rounds to 2 decimals |
| `raise ValueError(...)` | rejects a percent outside 0 to 100 |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python main.py` | runs `main.py` as the main program |
| `python -m shop.cart` | runs a module by its dotted name, as part of its package |
| `pwd` | prints the current directory |

### Errors

| Error | Means |
|---|---|
| `ModuleNotFoundError` | no folder on `sys.path` has the module, often from running in another directory |
| `ImportError` | an import that cannot complete, such as a relative import in a file run directly |
| `AttributeError` | a name not (yet) defined in a module, as in a circular import |
| `ValueError` | a discount percent below 0 or above 100 |

---

Every program so far has fitted in one file. Real programs do not: a file of
a few thousand lines is hard to find your way around, and code you wrote for
one program cannot be reused in another unless it lives somewhere both can
reach. Python's answer is to split code into **modules** (files) and group
related modules into **packages** (folders). This lesson covers how
`import` finds and loads them, and the few rules that keep a multi-file
program working.

## Modules

Every `.py` file is a **module**, and its name is the file name without
`.py`: the file `pricing.py` is the module `pricing`. Importing a module runs
the whole file, top to bottom, once, and gives you access to the names it
defined at its top level: its functions, classes and variables.

There are three common forms. They all load the module the same way; they
differ only in which names you get in your own file:

```python
import pricing                     # use as pricing.apply_discount(...)
from pricing import apply_discount # bring one name in
import pricing as p                # alias
```

(A sketch: these lines need a `pricing.py` beside them. The standard library
behaves the same way, and runs anywhere.)

```pycon
>>> import math
>>> math.sqrt(16)
4.0
>>> from math import pi
>>> round(pi, 2)
3.14
>>> import statistics as stats
>>> stats.mean([1, 2, 6])
3
```

- `import math` gives you one name, `math`, and you reach everything inside
  through it: `math.sqrt`. This keeps it obvious where each name came from.
- `from math import pi` copies one name into your file, so you write `pi`
  rather than `math.pi`. Good for a name you use constantly; with too many, a
  reader can no longer tell what came from where.
- `import statistics as stats` is the first form under a shorter name. Some
  aliases are near-universal conventions, such as `import numpy as np`.

Python keeps every imported module in a dict called `sys.modules`. A second
`import` of the same module, from anywhere in the program, finds it there and
does not run the file again; you get the same module object back. That is
why code at the top level of a module runs only once however many files
import it, and also why editing a file does not affect a running program
that has already imported it: you have to restart the program.

## Where Python looks

When you write `import pricing`, Python searches a list of folders for
`pricing.py` (or a `pricing` package) and uses the first one it finds. The
list is `sys.path`:

1. the folder of the script you ran (or the current directory, for
   `python -m` and the `>>>` prompt);
2. the standard library;
3. installed third-party packages.

So a file of your own called `random.py`, next to your script, wins over the
standard library's `random` module, and `import random` gets yours. Avoid
naming your files after standard modules.

If nothing matches, the import fails with `ModuleNotFoundError`. Most of
these puzzles come down to running from a different directory than you
think: the module is there, but not in a folder on `sys.path`. Checking
where you are (`pwd` in the terminal) and how you ran the program is the
first step.

## Packages

A **package** is a folder of modules with a file called `__init__.py` in it.
The package's name is the folder's name, and its modules are reached with a
dot: the file `shop/cart.py` is the module `shop.cart`.

```text
shop/
    __init__.py
    pricing.py
    cart.py
main.py
```

From `main.py`, either of these then works:

```python
from shop.cart import Cart
from shop import Cart          # works if __init__.py imports it
```

`__init__.py` runs when the package is first imported, before any of its
modules. It can be empty, but it is the natural place to define the
package's **public surface**: the names other code is meant to use. If it
imports them, callers can write `from shop import Cart` without needing to
know, or depend on, which file inside the package `Cart` lives in. You can
then reorganise the files later without breaking anyone:

```python
# shop/__init__.py
from .cart import Cart
from .pricing import apply_discount

__all__ = ["Cart", "apply_discount"]     # what `from shop import *` exports
```

`__all__` is a list of the public names as strings. It controls what
`from shop import *` brings in, and it tells readers and tools which names
are the package's intended interface. (`import *` itself is best avoided in
real code, since it makes it impossible to see where names came from.)

## Relative imports

Inside a package, one module often needs another from the same package. A
**relative import** names it by its position instead of by the full package
name: a leading `.` means "this package", and `..` means the package above it:

```python
# shop/cart.py
from .pricing import apply_discount
```

This reads "from the module `pricing` in my own package, import
`apply_discount`". The alternative, `from shop.pricing import apply_discount`,
also works, but it repeats the package name and breaks if the package is
ever renamed.

Relative imports only work in modules that were imported as part of a
package. A file run directly with `python shop/cart.py` is treated as a
lone script with no package around it, so `.pricing` has nothing to be
relative to:

```text
$ python shop/cart.py
Traceback (most recent call last):
  ...
ImportError: attempted relative import with no known parent package
```

Run package code as a module instead, with `python -m shop.cart` from the
folder that contains `shop`. `-m` tells Python to import it by its dotted
name, as part of its package.

## The __main__ guard

Every module has a variable `__name__` holding its name. For an imported
module it is the module's own name; for the file you ran directly, Python
sets it to the special value `"__main__"`:

```pycon
>>> import math
>>> math.__name__
'math'
>>> __name__              # the >>> prompt counts as the main program
'__main__'
```

That gives a file a way to tell how it is being used. Put the code that
should run only when the file is run as a program inside a `main()`
function, and call it under a check:

```python
def main():
    ...

if __name__ == "__main__":
    main()
```

Run as `python main.py`, the check is true and `main()` runs. Imported by
another file, or by a test, the check is false, so importing it only defines
`main` and does nothing else. Without the guard, every `import main` would
run the whole program as a side effect, printing output and doing work that
the importer never asked for. The guard makes a file usable both as a script
and as an importable module.

## Avoid circular imports

If `cart` imports `pricing` and `pricing` imports `cart`, you have a
**circular import**. When Python starts running `cart.py`, the first line
sends it off to run `pricing.py`, whose first line asks for `cart`, which is
only half run: the names further down `cart.py` do not exist yet. The result
is an `ImportError` or `AttributeError` that depends on which file happened
to be imported first. Keep dependencies pointing one way (here, `cart` uses
`pricing`, never the reverse), and move code both need into a third module
that imports neither.

## Your turn

The workspace has a `shop` package. Complete it:

- `shop/pricing.py`: the constant `TAX_RATE = 0.11` (already there), and
  `apply_discount(amount, percent)`, which returns `amount` with `percent`
  percent taken off: `apply_discount(200, 25)` is `150.0`. Any `percent`
  from 0 to 100 inclusive is allowed (0 changes nothing, 100 makes it free);
  a `percent` below 0 or above 100 raises `ValueError`.
- `shop/cart.py`: a `Cart` class with three methods. The starter keeps the
  items in `self.items`, a dict from name to `[price, qty]`.
  - `add(name, price, qty=1)` puts an item in the cart. Adding a name that is
    already there increases its quantity.
  - `count()` is the number of items, counting quantities: two pens and one
    ink is `3`.
  - `total(discount_percent=0)` is what the cart costs. Work it out in this
    order: add up price times quantity for every item, take the discount off
    that, add the tax (`TAX_RATE` of the discounted amount), and round to 2
    decimals. A cart holding 2 pens at 10 each has `total()` of `22.2` (20
    plus 11% tax) and `total(10)` of `19.98` (20 less 10% is 18, plus tax).
    An empty cart's total is `0`.

  Import `apply_discount` and `TAX_RATE` with a relative import; a test
  checks that `cart.py` contains `from .pricing import`.
- `shop/__init__.py`: expose `Cart`, `apply_discount` and `TAX_RATE`, and
  list exactly those three names in `__all__`.
- `main.py`: the starter builds a cart and prints its total with a 10%
  discount, but it does so at the top level, so it runs on import. Keep that
  same cart and the same printed total, and move the code into a `main()`
  function that runs only under the `__main__` guard. A test imports
  `main.py` and checks that nothing is printed until it calls `main()`.
