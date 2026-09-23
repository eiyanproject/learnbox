---
title: "Paper 3: data structures"
summary: List methods that return None, set algebra, inverting a dict, and the looping tools - enumerate, zip, sorted with a key.
order: 3
files: [structures.py]
run: python -i structures.py
hints:
  - "A `set` gives you the membership test, but sets have no order. Keep a `seen` set and append to a result list to preserve first-seen order."
  - "`setdefault(key, [])` returns the existing list or installs a new one, which is exactly what inverting a mapping needs."
  - "`sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))` sorts by score descending, then name ascending - a negative number flips one key without flipping the other."
  - "`enumerate(iterable, start=1)` gives 1-based positions, which is what a rank is."
---

Seven of the forty questions come from this section. The recurring theme is
*which methods return a value and which return `None`*.

## List methods mutate and return None

```python
values = [3, 1, 2]
values.sort()            # None - the list is now [1, 2, 3]
sorted(values)           # [1, 2, 3] - a new list, original untouched
```

`sort`, `reverse`, `append`, `extend`, `insert`, `remove` all return `None`.
`pop` is the exception: it returns the item it removed. `x = values.sort()`
leaving `x` as `None` is a classic exam question.

| Method | Returns |
| --- | --- |
| `append(x)`, `extend(it)`, `insert(i, x)` | `None` |
| `remove(x)`, `sort()`, `reverse()` | `None` |
| `pop()`, `pop(i)` | the removed item |
| `index(x)`, `count(x)` | an int |
| `copy()` | a **shallow** copy |

## Sets are algebra

```python
a, b = {1, 2, 3}, {3, 4}
a | b      # {1, 2, 3, 4}   union
a & b      # {3}            intersection
a - b      # {1, 2}         difference
a ^ b      # {1, 2, 4}      symmetric difference
```

`{}` is an empty **dict**, not an empty set — `set()` is the only way to write
that. Sets are unordered, so never assume the iteration order.

## Dicts, and the looping tools

```python
for key, value in mapping.items(): ...
for i, item in enumerate(values, start=1): ...
for a, b in zip(names, scores): ...
```

`zip` stops at the **shorter** input. `dict.get(key, default)` returns the
default instead of raising; `dict[key]` raises `KeyError`.
`setdefault(key, default)` returns the value, inserting the default first if
the key was missing.

## Your turn

In `structures.py`:

- `dedupe(values)`: the values with duplicates removed, **first occurrence
  order preserved**
- `invert(mapping)`: turn `{"a": 1, "b": 1, "c": 2}` into `{1: ["a", "b"], 2: ["c"]}`,
  with each list in sorted order
- `rank_scores(scores)`: given `{name: score}`, a list of `(rank, name, score)`
  tuples, highest score first, ties broken alphabetically, ranks starting at 1
- `set_report(a, b)`: a dict with keys `union`, `common`, `only_a` and
  `symmetric`, each a **sorted list**
