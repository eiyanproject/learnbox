---
title: "Paper 4: errors and exceptions"
summary: The order of try, except, else and finally; catching the right class; and raising your own.
order: 4
files: [errors.py]
run: python -i errors.py
hints:
  - "The clause order is fixed: `try`, then `except`, then `else`, then `finally`. `else` runs only when nothing was raised; `finally` runs either way."
  - "`parse_ints` should catch both `ValueError` (a bad string) and `TypeError` (something that is not a string or number) - `except (ValueError, TypeError):` catches a tuple of classes."
  - "A custom exception is a subclass: `class AgeError(ValueError): pass`. Because it subclasses `ValueError`, code catching `ValueError` still catches it."
  - "`raise AgeError(f\"...\")` - the message you pass becomes `str(err)`, which is what the test compares."
---

Four of the forty questions, and they are almost all about **order** and
**class**.

## Four clauses, one fixed order

```python
for text in ["42", "forty-two"]:
    try:
        int(text)
    except ValueError as err:
        print("failed:", err)
    else:
        print("no exception was raised")
    finally:
        print("always runs")
```

```output
no exception was raised
always runs
failed: invalid literal for int() with base 10: 'forty-two'
always runs
```

- `try` — the code being guarded
- `except` — runs **only** if a matching exception was raised
- `else` — runs **only** if none was raised
- `finally` — runs either way, including when the function returns from inside
  the `try`, and including when the exception is not caught at all

For `"42"`, `int()` succeeds, so `except` is skipped and `else` runs. For
`"forty-two"`, `int()` raises `ValueError`, so `except` runs and `else` is
skipped. `finally` runs both times. The clauses must be written in exactly
this order, and `else` needs at least one `except` before it; any other order
is a `SyntaxError`.

The `else` clause exists so the guarded block stays small. Code that should
only run when the `try` succeeded, but whose own errors you do *not* mean to
catch, belongs in `else`, not in `try`: an exception raised in `else` is not
handled by the `except` clauses above it.

## Catching the right class

Exceptions form a hierarchy. Catching a parent catches every child:

```
BaseException
 └── Exception
      ├── ArithmeticError  └── ZeroDivisionError
      ├── LookupError      ├── IndexError
      │                    └── KeyError
      ├── ValueError
      └── TypeError
```

So `except LookupError` catches both `IndexError` and `KeyError`. Catch several
unrelated classes with a tuple: `except (ValueError, TypeError):`.

```pycon
>>> for action in ([1, 2].__getitem__, {}.__getitem__):
...     try:
...         action(5)            # index 5 of a list, then key 5 of a dict
...     except LookupError as err:
...         print(type(err).__name__, "caught as LookupError")
...
IndexError caught as LookupError
KeyError caught as LookupError
>>> for item in ["x", None]:
...     try:
...         int(item)
...     except (ValueError, TypeError) as err:
...         print(type(err).__name__)
...
ValueError
TypeError
```

`int("x")` is a `ValueError` (a string, but not a number), and `int(None)` is
a `TypeError` (`None` is not something `int` can convert at all). One tuple
handles both.

Python checks the `except` clauses from the top and runs the first one that
matches, so a parent class listed above its child takes everything, and the
child's clause never runs. List the specific classes first.

A bare `except:` catches *everything*, including `KeyboardInterrupt`, which is
why it is considered a mistake rather than a shortcut.

## Raising your own

```pycon
>>> class AgeError(ValueError):
...     pass
...
>>> raise AgeError("age must not be negative")
Traceback (most recent call last):
  ...
AgeError: age must not be negative
>>> issubclass(AgeError, ValueError)     # so `except ValueError` catches it too
True
```

Subclassing `ValueError` rather than `Exception` means existing code that
already handles `ValueError` keeps working. The argument you pass becomes
`str(err)`.

## Your turn

In `errors.py`:

- `safe_divide(a, b)`: `a / b`, or the string `"undefined"` when `b` is zero:
  `safe_divide(7, 2)` is `3.5`
- `parse_ints(items)`: try `int()` on every item and keep the results,
  skipping any item it raises for: `["1", "x", 2, None]` gives `[1, 2]`
  (`"x"` raises `ValueError` and `None` raises `TypeError`). A float is cut
  down to a whole number, as `int()` does: `[1.9]` gives `[1]`.
- `trace_order(should_raise)`: write one `try` statement with all four
  clauses - `try`, `except`, `else`, `finally` - and have each clause append
  its own name to a list as it runs. Inside the `try`, raise an exception
  when `should_raise` is true. Return the list: it is
  `["try", "except", "finally"]` when it raises and
  `["try", "else", "finally"]` when it does not.
- `AgeError`, a subclass of `ValueError`, and `validate_age(age)`, which
  returns the age when it is zero or more and raises `AgeError` with the
  message `"age must not be negative"` otherwise
