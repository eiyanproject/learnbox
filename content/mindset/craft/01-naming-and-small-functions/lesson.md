---
title: Naming and small functions
summary: Names as the cheapest documentation there is, and the length at which a function stops being readable.
order: 1
files: [clean.py]
run: python -i clean.py
hints:
  - "`days_until_expiry` replaces `d`: the test calls the new names, so renaming is the exercise, not an optional tidy-up."
  - "`is_expired` and `is_expiring_soon` are separate predicates - one condition each, named for what they mean."
  - "`categorise` should read as a summary: three or four lines using the predicates, no arithmetic of its own."
  - "Return the strings exactly: \"expired\", \"expiring soon\", \"fresh\"."
---

Code is read far more often than it is written, usually by someone with less
context than the author had — frequently the author, months later.

## Names carry the explanation

```python
def f(d, t):
    if d < 0:
        return "e"
    elif d < t:
        return "s"
    return "f"
```

Correct, and unreadable. Every reader must reconstruct the meaning from
context, every time.

```python
def categorise(days_until_expiry, warning_days):
    if is_expired(days_until_expiry):
        return "expired"
    if is_expiring_soon(days_until_expiry, warning_days):
        return "expiring soon"
    return "fresh"
```

Same logic, no comment needed. The names did the documenting, and unlike a
comment they cannot drift out of date without the code changing too.

## Rules that survive contact

- **Length should match scope.** `i` in a three-line loop is fine. `d` as a
  parameter crossing a function boundary is not.
- **Booleans read as questions.** `is_expired`, `has_permission`,
  `should_retry`. A name like `flag` or `status` tells you nothing about which
  way `True` points.
- **Avoid the type in the name.** `user_list` becomes wrong the day it is a
  set. `users` stays right.
- **Say what, not how.** `get_users_from_db_with_join` promises an
  implementation; `find_active_users` promises a result.

## Small functions

If a function does not fit on a screen, you cannot see it. The practical limit
is where you stop being able to hold it in your head.

Size is a symptom rather than the disease: a long function is usually several
functions that were never named. Extract a piece, name it honestly, and the
original gets shorter *and* clearer.

Watch for these signals:

- comments introducing sections — each section is a function with a name
  already written
- a nesting level of three or more
- the word "and" in an honest description

## The one comment worth writing

Not what the code does — the code says that. **Why** it does it that way:

```python
# The API returns 429 without a Retry-After header, so back off by hand.
```

That is information the code cannot carry, and the reason it will not be
"simplified" back into a bug next year.

## Your turn

`clean.py` has correct, unreadable code. Rewrite it with:

- `days_until_expiry` and `warning_days` as parameter names
- `is_expired(days_until_expiry)` — expired when negative
- `is_expiring_soon(days_until_expiry, warning_days)` — within the warning
  window and not already expired
- `categorise(days_until_expiry, warning_days)` — `"expired"`,
  `"expiring soon"` or `"fresh"`, reading as a summary of the predicates
