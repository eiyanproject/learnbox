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

- `shop/pricing.py`: `TAX_RATE = 0.11` and `apply_discount(amount, percent)`
  returning `amount` reduced by `percent`% (0 to 100, otherwise `ValueError`)
- `shop/cart.py`: `Cart` with `add(name, price, qty=1)` (adding the same name
  again increases its quantity), `count()` (total items) and
  `total(discount_percent=0)`: subtotal, then discount, then tax, rounded to 2
  decimals. Import `apply_discount` and `TAX_RATE` relatively.
- `shop/__init__.py`: expose `Cart`, `apply_discount` and `TAX_RATE`, with `__all__`
- `main.py`: a `main()` that prints the total of a small cart, run only under
  the `__main__` guard
