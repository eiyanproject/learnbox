---
title: "Round 3: Find the culprit"
summary: Something broke between two versions, and some part of a big input triggers it. Two searches that find the cause without guessing.
order: 3
files: [culprit.py]
run: python -i culprit.py
challenge:
  minutes: 20
  xp: 250
  requires:
    xp: 200
---

Version 1 worked and version 800 does not. Somewhere in a 60-line input is
the line that crashes the importer. Guessing is not a method; searching is.

## The task

In `culprit.py`, write two functions.

### `first_bad(n, is_bad)`

Versions are numbered `1` to `n`. `is_bad(version)` returns `True` or
`False`, and once a version is bad every later one is bad too. Return the
**first bad version**, or `None` if even version `n` is good.

Each call of `is_bad` stands for a slow build, so the tests count them: you
may call it at most `n.bit_length() + 1` times. Checking the versions one by
one will not do; halve the range each time.

```text
first_bad(8, is_bad) where versions 6, 7, 8 are bad   ->  6
first_bad(8, is_bad) where nothing is bad             ->  None
```

### `minimal_failing(items, fails)`

`items` is a list for which `fails(items)` is `True`. Return a smaller list
that still fails, cut down as far as this procedure goes:

1. Go through the positions from first to last.
2. At each one, try the list **without** that item. If `fails` is still
   `True`, keep the shorter list and try the item now at that position;
   otherwise put the item back and move to the next position.
3. Stop after the last position.

The result is a list in the original order from which no single item can be
removed without the failure going away. Do not change the list you were
given.

```text
fails = "the list contains both 3 and 7"
minimal_failing([1, 3, 5, 7, 9], fails)   ->  [3, 7]
```
