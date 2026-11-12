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
Python has no separate procedure form (some languages distinguish functions,
which return a value, from procedures, which only do something; in Python
every function returns something, `None` if nothing else).

```pycon
>>> def forgot(x):
...     x * 2                 # computed, then thrown away
...
>>> print(forgot(4))
None
```

Validating early is the house style — check the arguments, raise, and let the
rest of the body assume everything is fine:

```python
def apply_discount(price, percent):
    if price < 0:
        raise ValueError("price must not be negative")
    ...
```

The alternative, returning a special value like `-1` for failure, forces every
caller to remember to check, and a caller who forgets carries on with `-1` as
if it were a real price. An exception cannot be ignored by accident: if
nobody catches it, the program stops and says why.

Two details the exam asks about:

- `raise ValueError("message")` — the message is what `str(err)` gives back,
  and it is what `pytest.raises(...)` inspects.
- A bare `except:` catches `BaseException`, which includes `KeyboardInterrupt`
  and `SystemExit`. Catching `Exception` leaves those alone so Ctrl-C still
  works. Always name what you are catching.

```pycon
>>> def attempt_demo():
...     try:
...         raise ValueError("price must not be negative")
...     except ValueError as err:
...         return str(err)
...
>>> attempt_demo()
'price must not be negative'
```

Guarding against a division by zero by checking the input first is usually
better than catching `ZeroDivisionError` afterwards, because the check says
what the code expects rather than what went wrong.

## Your turn

In `guarded.py`:

- `apply_discount(price, percent)`: the price with `percent` percent taken
  off, rounded to 2 decimals: `apply_discount(80, 25)` is `60.0`, and
  `apply_discount(19.99, 15)` is `16.99`. Raise
  `ValueError("price must not be negative")` for a negative price, and
  `ValueError("percent must be between 0 and 100")` for a percent outside that
  range; 0 and 100 themselves are allowed. The messages must match exactly.
- `average(*numbers)`: the mean of the arguments, and `0.0` when there are
  none (rather than dividing by zero).
- `safe_get(mapping, keys, default=None)`: `mapping` is a dict that may hold
  more dicts, and `keys` is a list. Look up the first key in `mapping`, the
  second key in what that gave you, and so on, and return what the last key
  leads to. If a key is missing, or you land on something that is not a dict
  before the keys run out, return `default`. With `d = {"a": {"b": 1}}`,
  `safe_get(d, ["a", "b"])` is `1` and `safe_get(d, ["a", "x"], 0)` is `0`.
  The last key may lead to a dict, which is returned as it is
  (`safe_get(d, ["a"])` is `{"b": 1}`), and an empty `keys` list returns
  `mapping` itself.
- `attempt(func, fallback)`: call `func()` with no arguments and return its
  result, or `fallback` if it raises an `Exception`.
