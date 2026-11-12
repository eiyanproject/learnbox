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

```pycon
>>> values = [1, 2, 2]
>>> [x * 2 for x in values]          # list
[2, 4, 4]
>>> {x * 2 for x in values}          # set: the duplicate is gone
{2, 4}
>>> pairs = [("a", 1), ("b", 2)]
>>> {k: v for k, v in pairs}         # dict
{'a': 1, 'b': 2}
>>> (x * 2 for x in values)          # generator - lazy, not a tuple
<generator object <genexpr> at 0x...>
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

`zip(*matrix)` deserves a closer look, because it combines two ideas. The
`*` unpacks the matrix, passing each row as a separate argument, so for a
two-row matrix it is `zip(row0, row1)`. `zip` then takes the first item of
every row, then the second of every row, and so on, which are exactly the
columns:

```pycon
>>> matrix = [[1, 2, 3], [4, 5, 6]]
>>> list(zip(*matrix))                 # the same as zip([1, 2, 3], [4, 5, 6])
[(1, 4), (2, 5), (3, 6)]
>>> [list(col) for col in zip(*matrix)]
[[1, 4], [2, 5], [3, 6]]
```

And shallow immutability in action:

```pycon
>>> t = ("tags", ["a"])
>>> t[1].append("b")         # the list inside can change...
>>> t
('tags', ['a', 'b'])
>>> t[1] = []                # ...but the tuple's own slots cannot
Traceback (most recent call last):
  ...
TypeError: 'tuple' object does not support item assignment
```

## Your turn

In `collections_review.py`:

- `word_frequency(text)`: a dict of lowercase word to count, splitting on
  any whitespace: `"The cat the Hat"` gives `{"the": 2, "cat": 1, "hat": 1}`,
  extra spaces make no difference, and an empty text gives `{}`.
- `group_by_length(words)`: a dict of word length to the sorted list of words
  with that length: `["pear", "fig", "kiwi", "plum"]` gives
  `{4: ["kiwi", "pear", "plum"], 3: ["fig"]}`
- `transpose(matrix)`: swap rows and columns, returning a list of lists (not
  tuples): `[[1, 2, 3], [4, 5, 6]]` gives `[[1, 4], [2, 5], [3, 6]]`.
  Transposing twice gives back the original.
- `common_items(a, b)`: a sorted list of the items appearing in both, each
  listed once: `[3, 1, 2, 3]` and `[3, 2, 5]` give `[2, 3]`
