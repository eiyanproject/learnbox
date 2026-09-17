---
title: Errors and exceptions
summary: Read a traceback, catch what you expect, raise your own errors with useful messages.
order: 10
files: [errors.py]
run: python -i errors.py
hints:
  - "`safe_divide`: `try: return a / b` then `except ZeroDivisionError: return None`."
  - "`parse_age`: `int(text)` raises `ValueError` for non-numbers. Let it, or catch it and `raise ValueError(...)` with your own message. Then check the range and `raise ValueError(\"age out of range\")`."
  - "`total_valid_prices`: loop, `try: total += float(item)`, `except ValueError: skipped += 1`, and return both."
  - "`withdraw` must check before changing anything: `if amount <= 0: raise ValueError(...)`, `if amount > balance: raise InsufficientFunds(...)`."
---

When something goes wrong, Python **raises an exception** and, unless
something catches it, stops with a **traceback**:

```pytb
Traceback (most recent call last):
  File "shop.py", line 7, in <module>
    total = checkout(cart)
  File "shop.py", line 3, in checkout
    return price / quantity
ZeroDivisionError: division by zero
```

Read a traceback **from the bottom up**. The last line names the error and
says what happened; the lines above it show where, with the innermost call
last.

## Common exceptions

| Exception | Typical cause |
|---|---|
| `ValueError` | right type, wrong value: `int("abc")` |
| `TypeError` | wrong type: `"2" + 2` |
| `KeyError` | missing dict key |
| `IndexError` | list position past the end |
| `ZeroDivisionError` | dividing by zero |
| `FileNotFoundError` | opening a file that is not there |
| `AttributeError` | calling a method a value does not have |

## try and except

Catch an exception you expect and can do something sensible about:

```python
try:
    quantity = int(text)
except ValueError:
    quantity = 1
```

Several handlers, plus `else` (runs if nothing was raised) and `finally`
(always runs):

```python
try:
    value = data[key] / count
except KeyError:
    value = 0
except ZeroDivisionError:
    value = None
else:
    print("computed fine")
finally:
    print("done either way")
```

`except ValueError as e:` gives you the exception object; `str(e)` is its
message.

Catch the specific exception you expect. A bare `except:` also swallows
typos and Ctrl+C, and hides real bugs.

## Raising your own

```python
def set_volume(level):
    if not 0 <= level <= 10:
        raise ValueError(f"volume must be 0-10, got {level}")
    ...
```

A good message says what was expected and what arrived.

## Custom exception types

Subclass `Exception` when callers need to tell your error apart from others:

```python
class OutOfStock(Exception):
    pass

raise OutOfStock("no mangoes left")
```

## Checking before, or asking forgiveness

Both styles are fine. `if key in d:` checks first. `try: d[key]` just tries.
Python code often prefers trying, especially when the check would repeat
work or could race with something else changing the data.

## Your turn

In `errors.py`, write:

- `safe_divide(a, b)`: `a / b`, or `None` when `b` is zero
- `parse_age(text)`: the text as an `int`. Raise `ValueError` if it is not a
  whole number, or if it is below 0 or above 150.
- `total_valid_prices(items)`: add up every item that `float()` can convert
  and skip the rest. Return `(total, skipped_count)`, total rounded to 2 decimals.
- `withdraw(balance, amount)`: return the new balance. Raise `ValueError` if
  `amount` is not positive, and the provided `InsufficientFunds` if it is more
  than the balance.
