---
title: "Review 4: a class that saves itself"
summary: Lessons 11 and 12 together - a small class that keeps records, writes them to a file and reads them back.
order: 4
files: [ledger.py]
run: python -i ledger.py
hints:
  - "Give each `Ledger` its own list in `__init__` (`self.entries = []`). A list assigned in the class body would be shared by every ledger ever made - the same trap as a mutable default argument."
  - "`total` is `sum(amount for _, amount in self.entries)`. Summing an empty sequence gives `0`, which is the right answer for an empty ledger."
  - "`top_spender`: total each name into a dict first. Then sort the `(name, total)` pairs with `key=lambda kv: (-kv[1], kv[0])` (highest total first, ties alphabetical) and take the first name. `max` with a key could find the highest total, but breaking the tie alphabetically inside `max` gets awkward."
  - "`load` is a `@classmethod`: it builds a new `Ledger`, calls `add` for each line, and returns it. Split each line on the comma and convert the amount with `float`."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **ledger** | a record of entries, here a name and an amount each |
| **state** | the data an object holds |
| **class body** | the lines directly under `class`; anything assigned there is shared by every instance |
| **instance attribute** | assigned to `self` in `__init__`; one per object |
| **shared-list trap** | a list in the class body used by every instance, like a mutable default argument |
| **class method** | receives the class (`cls`) instead of an instance |
| **alternative constructor** | a class method that builds an object another way, here from a file |
| **truncate** | empty the file before writing (mode `"w"`) |
| **tie-break** | the rule for equal totals: alphabetically first wins |

### Python names and functions

| Name | What it does |
|---|---|
| `def __init__(self): self.entries = []` | a fresh list per object |
| `@classmethod def load(cls, path):` | builds with `cls()`, so subclasses get their own type |
| `with open(path, "w") as f:` | writes a file, closing it even after an error |
| `f.write(f"{name},{amount}\n")` | one `name,amount` line |
| `line.strip().split(",")` | removes the newline, then splits at the comma |
| `float(text)` | text from a file turned into a number |
| `sum(...)` | the total |
| `min(totals, key=lambda n: (-totals[n], n))` | one way to pick the biggest total, alphabetically first on a tie |

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
and it is equally popular in exams:

```pycon
>>> class Wrong:
...     entries = []
...
>>> a, b = Wrong(), Wrong()
>>> a.entries.append("x")    # no assignment, so this finds the class's list
>>> b.entries                # ...which b shares
['x']
```

`a.entries.append(...)` does not assign to `a.entries`; it reads it, finds
no list on `a` itself, falls back to the one on the class, and changes that.

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

- `__init__()`: an empty ledger. Each ledger keeps its own list of entries,
  not one shared between them.
- `add(name, amount)`: record one entry
- `total()`: the sum of every amount, `0` when empty
- `top_spender()`: the name whose entries add up to the most. If two names
  are level, the one that comes first alphabetically wins. `None` when the
  ledger is empty.
- `save(path)`: write the entries to a file, one `name,amount` line each, in
  the order they were added, with the amount as Python prints it: an entry of
  `("ana", 10)` and one of `("budi", 5.5)` give the lines `ana,10` and
  `budi,5.5`. Saving replaces whatever the file held before.
- `load(path)`: a **classmethod** that reads a file written by `save` and
  returns a new `Ledger` holding the same entries (convert each amount with
  `float()`, since it comes back as text). Loading a file saved from an
  empty ledger gives an empty ledger.
