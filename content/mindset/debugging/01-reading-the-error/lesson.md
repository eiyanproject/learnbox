---
title: Reading the error
summary: The traceback is not noise - it names the failure, the value and the line, and reading it in the right order answers most questions before you look at the code.
order: 1
files: [fix_me.py]
run: python -i fix_me.py
hints:
  - "Each function here has one bug matching the error in its docstring. Do not rewrite them - find the one wrong thing."
  - "`average` divides by zero on an empty list; decide what an empty average means and handle it explicitly rather than letting it throw."
  - "`get_first_word` fails on an empty string because split() returns an empty list - index 0 does not exist."
  - "`total_price` gets a TypeError because one quantity arrives as a string: convert with int() before multiplying."
---

A traceback looks like a wall of text and is actually a structured report. Read
it in this order:

**1. The last line — what went wrong**

```
ZeroDivisionError: division by zero
```

The exception type is a category and the message is the specific case. Two
seconds here saves minutes of guessing.

**2. The bottom of the stack — where**

Tracebacks read oldest-call-first, so the line that actually failed is at the
**bottom**, just above the error. Everything above is how you got there.

**3. Your code in the middle**

When the failing line is inside a library, scan upward for the last frame in a
file you wrote. That is usually where the wrong value came from — the library
merely noticed.

## What the common ones actually mean

| Error | Means |
|---|---|
| `NameError` | the name does not exist — typo, or not yet assigned |
| `AttributeError: 'NoneType' has no attribute 'x'` | something returned `None`, likely a function with no `return` |
| `IndexError` / `KeyError` | the container is smaller or different than you assume |
| `TypeError` | the value is not the type you think — often a string where a number is expected |
| `ZeroDivisionError` | a count was zero; usually an empty collection |

`'NoneType' object has no attribute` is worth memorising: it almost always
means a function fell off the end without returning.

## The value matters more than the line

"Why did this line fail?" is usually the wrong question. The line is fine; the
**value** reaching it is wrong. The useful question is *where did this value
come from*, and the answer is upward in the traceback, not in the failing line.

## Fix the cause, not the symptom

Wrapping the failing line in `try/except` makes the message go away and leaves
the wrong value in place, to surface later somewhere with no traceback at all.
Ask what *should* happen for this input, and make that happen.

## Your turn

`fix_me.py` has four functions, each with one bug and the error it produces in
its docstring. Fix the cause in each:

- `average(values)` — `ZeroDivisionError` on an empty list; an empty average
  should be `0`
- `get_first_word(text)` — `IndexError` on an empty or blank string; should
  return `""`
- `total_price(items)` — `TypeError` when a quantity arrives as a string
- `find_user(users, name)` — `AttributeError` because it forgets to return
