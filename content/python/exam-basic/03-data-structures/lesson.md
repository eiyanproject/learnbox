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

```pycon
>>> values = [3, 1, 2]
>>> print(values.sort())     # sorts in place and returns None
None
>>> values
[1, 2, 3]
>>> other = [9, 7, 8]
>>> sorted(other)            # a new list...
[7, 8, 9]
>>> other                    # ...and the original is untouched
[9, 7, 8]
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

```pycon
>>> a, b = {1, 2, 3}, {3, 4}
>>> a | b      # union
{1, 2, 3, 4}
>>> a & b      # intersection
{3}
>>> a - b      # difference
{1, 2}
>>> a ^ b      # symmetric difference: in one but not both
{1, 2, 4}
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

- `dedupe(values)`: the values with duplicates removed, keeping each value
  where it **first** appeared: `[3, 1, 3, 2, 1]` gives `[3, 1, 2]`
- `invert(mapping)`: a dict from each value to the list of keys that had it.
  `{"a": 1, "b": 1, "c": 2}` gives `{1: ["a", "b"], 2: ["c"]}`, with each
  list in sorted order.
- `rank_scores(scores)`: `scores` is a dict of name to score. Return a list of
  `(rank, name, score)` tuples, highest score first. Equal scores go in
  alphabetical order of name, and still get different ranks: the rank is just
  the position in the list, starting at 1.
  `{"bo": 70, "ana": 90, "cy": 70}` gives
  `[(1, "ana", 90), (2, "bo", 70), (3, "cy", 70)]`.
- `set_report(a, b)`: compare two lists as sets. Return a dict with four
  keys, each a **sorted list**: `union` (in either), `common` (in both),
  `only_a` (in `a` and not in `b`) and `symmetric` (in exactly one of them).
  `set_report([1, 2, 3], [3, 4])` is
  `{"union": [1, 2, 3, 4], "common": [3], "only_a": [1, 2], "symmetric": [1, 2, 4]}`.
