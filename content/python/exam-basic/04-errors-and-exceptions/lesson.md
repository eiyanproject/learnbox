---
title: "Paper 4: errors and exceptions"
summary: The order of try, except, else and finally; catching the right class; and raising your own.
order: 4
files: [errors.py]
run: python -i errors.py
hints:
  - "The clause order is fixed: `try`, then `except`, then `else`, then `finally`. `else` runs only when nothing was raised; `finally` runs either way."
  - "`parse_ints` should catch both `ValueError` (a bad string) and `TypeError` (something that is not a string or number) - `except (ValueError, TypeError):` catches a tuple of classes."
  - "A custom exception is just a subclass: `class AgeError(ValueError): pass`. Because it subclasses `ValueError`, code catching `ValueError` still catches it."
  - "`raise AgeError(f\"...\")` - the message you pass becomes `str(err)`, which is what the test compares."
---

Four of the forty questions, and they are almost all about **order** and
**class**.

## Four clauses, one fixed order

```python
try:
    risky()
except ValueError as err:
    print("failed:", err)
else:
    print("no exception was raised")
finally:
    print("always runs")
```

- `try` — the code being guarded
- `except` — runs **only** if a matching exception was raised
- `else` — runs **only** if none was raised
- `finally` — runs either way, including when the function returns from inside
  the `try`, and including when the exception is not caught at all

The `else` clause exists so the guarded block stays small. Code that can't
raise belongs in `else`, not in `try`.

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

A bare `except:` catches *everything*, including `KeyboardInterrupt`, which is
why it is considered a mistake rather than a shortcut.

## Raising your own

```python
class AgeError(ValueError):
    pass

raise AgeError("age must not be negative")
```

Subclassing `ValueError` rather than `Exception` means existing code that
already handles `ValueError` keeps working. The argument you pass becomes
`str(err)`.

## Your turn

In `errors.py`:

- `safe_divide(a, b)`: `a / b`, or the string `"undefined"` when `b` is zero
- `parse_ints(items)`: every item that converts to `int`, skipping any that
  raises — `["1", "x", 2, None]` gives `[1, 2]`
- `trace_order(should_raise)`: a list of the clause names visited, in order —
  `["try", "except", "finally"]` when it raises, `["try", "else", "finally"]`
  when it does not
- `AgeError`, a subclass of `ValueError`, and `validate_age(age)` which raises
  it with the message `"age must not be negative"` for a negative age, and
  returns the age otherwise
