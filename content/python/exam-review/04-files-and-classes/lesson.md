---
title: "Review 4: a class that saves itself"
summary: Lessons 11 and 12 together - a small class that keeps records, writes them to a file and reads them back.
order: 4
files: [ledger.py]
run: python -i ledger.py
hints:
  - "Give each `Ledger` its own list in `__init__` (`self.entries = []`). A list assigned in the class body would be shared by every ledger ever made - the same trap as a mutable default argument."
  - "`total` is `sum(amount for _, amount in self.entries)`. Summing an empty sequence gives `0`, which is the right answer for an empty ledger."
  - "`top_spender`: total each name into a dict first, then `min`/`max` with a key. `max(totals.items(), key=lambda kv: (kv[1], [-ord(c) for c in kv[0]]))` is unreadable - sort instead, with `key=lambda kv: (-kv[1], kv[0])`, and take the first."
  - "`load` is a `@classmethod`: it builds a new `Ledger`, calls `add` for each line, and returns it. Split each line on the comma and convert the amount with `float`."
---

The last review puts lessons 11 and 12 together, because in real code they
always arrive together: an object that holds state, and the file that state
survives in.

## Worth re-reading first

Anything assigned in the **class body** is shared by every instance. Anything
assigned to `self` in `__init__` belongs to that one object:

```python
class Wrong:
    entries = []          # one list, shared by every Wrong ever created

class Right:
    def __init__(self):
        self.entries = [] # a fresh list per object
```

This is the same bug as the mutable default argument, wearing a different hat,
and it is just as popular in exams.

A `@classmethod` receives the class rather than an instance, which is how you
write an alternative constructor:

```python
@classmethod
def load(cls, path):
    ledger = cls()
    ...
    return ledger
```

Using `cls()` rather than `Ledger()` means a subclass gets its own type back.

For the file half: `with open(...)` closes on the way out even if the body
raises, `"w"` truncates, and every line you read back carries its `"\n"` until
you strip it. Text read from a file is always `str` — `"12.5"` needs `float()`
before it can be added to anything.

## Your turn

In `ledger.py`, a `Ledger` class with:

- `__init__()`: an empty ledger, each with its own entry list
- `add(name, amount)`: record one entry
- `total()`: the sum of every amount, `0` when empty
- `top_spender()`: the name with the highest total, ties broken alphabetically,
  and `None` when the ledger is empty
- `save(path)`: one `name,amount` line per entry
- `load(path)`: a **classmethod** returning a new `Ledger` built from that file
