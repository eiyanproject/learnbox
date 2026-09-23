---
title: "Review 2: collections and comprehensions"
summary: Lessons 7 to 9 mixed - lists, tuples, dicts, sets and the comprehensions that build them.
order: 2
files: [collections_review.py]
run: python -i collections_review.py
hints:
  - "`word_frequency`: lowercase the whole text once, then `split()`. `counts[word] = counts.get(word, 0) + 1` avoids a KeyError on the first sighting."
  - "`group_by_length`: `groups.setdefault(len(word), []).append(word)`, then sort each list at the end."
  - "`transpose` is `[list(row) for row in zip(*matrix)]` - `zip(*matrix)` passes each row as a separate argument, which pairs the columns up."
  - "`common_items` is set intersection, sorted: `sorted(set(a) & set(b))`."
---

Lessons 7 through 9, shuffled: lists and tuples, dicts and sets, and
comprehensions.

## Worth re-reading first

A **comprehension** builds a new collection in one expression, and the brackets
decide what kind:

```python
[x * 2 for x in values]          # list
{x * 2 for x in values}          # set
{k: v for k, v in pairs}         # dict
(x * 2 for x in values)          # generator - lazy, not a tuple
```

There is no tuple comprehension; round brackets give you a generator that
yields one item at a time and is exhausted after one pass.

Other places marks get lost:

- `dict.get(key, default)` returns the default; `dict[key]` raises `KeyError`.
- `setdefault(key, [])` returns the list already stored under `key`, or
  installs the new one and returns that — the standard way to group.
- Sets discard duplicates **and** order. Sorting the result is what makes a
  set-based answer testable.
- `zip` stops at the shortest input and returns tuples, so a transposed matrix
  needs `list(row)` if you want lists back.
- A tuple is immutable, but a tuple *containing* a list can still have that
  list modified — immutability is shallow.

## Your turn

In `collections_review.py`:

- `word_frequency(text)`: a dict of lowercase word to count, splitting on
  whitespace
- `group_by_length(words)`: a dict of word length to the sorted list of words
  with that length
- `transpose(matrix)`: swap rows and columns, returning a list of lists
- `common_items(a, b)`: a sorted list of the items appearing in both
