---
title: "Review 3: functions and failure"
summary: Lessons 3 and 10 mixed - arguments, defaults and return values, and the exceptions that interrupt them.
order: 3
files: [guarded.py]
run: python -i guarded.py
hints:
  - "`apply_discount` validates before it calculates. Raise `ValueError` with the exact messages the lesson lists, then return `round(price * (1 - percent / 100), 2)`."
  - "`average` must not divide by zero. Check for an empty argument list first and return `0.0`."
  - "`safe_get` walks the keys one at a time. After each step, if the current value is not a dict, there is nothing left to walk - return the default."
  - "`attempt` catches `Exception`, not bare `except:` - the bare form would also swallow KeyboardInterrupt."
---

Lessons 3 and 10, mixed: defining functions, and what happens when they refuse
to finish.

## Worth re-reading first

A function returns `None` if it falls off the end without a `return`. That is
the source of most "why is my result None" confusion, and it is deliberate:
Python has no separate procedure form.

Validating early is the house style — check the arguments, raise, and let the
rest of the body assume everything is fine:

```python
def apply_discount(price, percent):
    if price < 0:
        raise ValueError("price must not be negative")
    ...
```

The alternative, returning a special value like `-1` for failure, forces every
caller to remember to check. An exception cannot be ignored by accident.

Two details the exam asks about:

- `raise ValueError("message")` — the message is what `str(err)` gives back,
  and it is what `pytest.raises(...)` inspects.
- A bare `except:` catches `BaseException`, which includes `KeyboardInterrupt`
  and `SystemExit`. Catching `Exception` leaves those alone so Ctrl-C still
  works. Always name what you are catching.

Guarding against a division by zero by checking the input first is usually
better than catching `ZeroDivisionError` afterwards, because the check says
what the code expects rather than what went wrong.

## Your turn

In `guarded.py`:

- `apply_discount(price, percent)`: the discounted price rounded to 2 decimals.
  Raise `ValueError("price must not be negative")` for a negative price, and
  `ValueError("percent must be between 0 and 100")` for a percent outside that
  range
- `average(*numbers)`: the mean of the arguments, and `0.0` when there are none
- `safe_get(mapping, keys, default=None)`: walk the nested dict following
  `keys` in order, returning `default` if any step is missing or not a dict
- `attempt(func, fallback)`: call `func()` and return its result, or `fallback`
  if it raises an `Exception`
