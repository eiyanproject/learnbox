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

## Modules

Every `.py` file is a **module**. Importing it runs the file once and gives
you its top-level names:

```python
import pricing                     # use as pricing.apply_discount(...)
from pricing import apply_discount # bring one name in
import pricing as p                # alias
```

Python caches imported modules in `sys.modules`, so a second import of the same
module does not run it again.

## Where Python looks

`sys.path` lists the folders searched, starting with the folder of the script
you ran (or the current directory for `python -m` and the REPL), then the
standard library and installed packages. Most "ModuleNotFoundError" puzzles
come down to running from a different directory than you think.

## Packages

A **package** is a folder of modules with an `__init__.py`:

```
shop/
    __init__.py
    pricing.py
    cart.py
main.py
```

```python
from shop.cart import Cart
from shop import Cart          # works if __init__.py imports it
```

`__init__.py` runs when the package is first imported. Use it to define the
package's public surface, so users do not need to know your file layout:

```python
# shop/__init__.py
from .cart import Cart
from .pricing import apply_discount

__all__ = ["Cart", "apply_discount"]     # what `from shop import *` exports
```

## Relative imports

Inside a package, `.` means "this package" and `..` its parent:

```python
# shop/cart.py
from .pricing import apply_discount
```

Relative imports only work in modules imported as part of a package, not in a
file run directly with `python shop/cart.py`. Run package code with
`python -m shop.cart` instead.

## The __main__ guard

When a file is run directly, its `__name__` is `"__main__"`; when imported,
it is the module name. So:

```python
def main():
    ...

if __name__ == "__main__":
    main()
```

makes a file usable both as a script and as an importable module without its
script behaviour running on import.

## Avoid circular imports

If `cart` imports `pricing` and `pricing` imports `cart`, one of them sees a
half-initialised module. Keep dependencies pointing one way; move shared code
into a third module.

## Your turn

The workspace has a `shop` package. Complete it:

- `shop/pricing.py`: the constant `TAX_RATE = 0.11`, and
  `apply_discount(amount, percent)`, which returns `amount` with `percent`
  percent taken off: `apply_discount(200, 25)` is `150.0`. A `percent` below
  0 or above 100 raises `ValueError`.
- `shop/cart.py`: a `Cart` class with three methods.
  - `add(name, price, qty=1)` puts an item in the cart. Adding a name that is
    already there increases its quantity.
  - `count()` is the number of items, counting quantities: two pens and one
    ink is `3`.
  - `total(discount_percent=0)` is what the cart costs. Work it out in this
    order: add up price times quantity for every item, take the discount off
    that, add the tax (`TAX_RATE` of the discounted amount), and round to 2
    decimals. A cart holding 2 pens at 10 each has `total()` of `22.2` (20
    plus 11% tax) and `total(10)` of `19.98` (20 less 10% is 18, plus tax).

  Import `apply_discount` and `TAX_RATE` with a relative import.
- `shop/__init__.py`: expose `Cart`, `apply_discount` and `TAX_RATE`, with `__all__`
- `main.py`: a `main()` that prints the total of a small cart, run only under
  the `__main__` guard
