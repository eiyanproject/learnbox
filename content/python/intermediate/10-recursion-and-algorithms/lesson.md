---
title: Recursion and algorithms
summary: Think recursively, memoise overlapping work, search sorted data in O(log n), and reason about complexity.
order: 10
files: [algorithms.py]
run: python -i algorithms.py
hints:
  - "`flatten`: for each item, `if isinstance(item, list): result.extend(flatten(item))`, else append it."
  - "`binary_search`: keep `lo, hi = 0, len(items) - 1`; while `lo <= hi`, compare `items[mid]` with the target and move one bound past `mid`."
  - "`permutations(items)`: for each index `i`, take `items[i]` as the first element and prepend it to every permutation of the rest, `items[:i] + items[i+1:]`. The base case is one empty permutation."
  - "`count_paths(rows, cols)`: `@functools.cache`; a 1-row or 1-column grid has one path; otherwise it is `count_paths(r - 1, c) + count_paths(r, c - 1)`."
---

## Recursion

A **recursive** function solves a problem by calling itself on a smaller
version of it. Every recursive function needs:

1. a **base case** that answers directly, and
2. a **recursive case** that moves towards the base case.

```python
def factorial(n):
    if n <= 1:              # base case
        return 1
    return n * factorial(n - 1)
```

Recursion fits naturally on data that is itself recursive: nested lists, trees,
file systems, expressions.

```python
def total_size(folder):
    return sum(total_size(x) if x.is_dir() else x.stat().st_size for x in folder.iterdir())
```

Python limits recursion depth (about 1000 frames, `sys.getrecursionlimit()`).
Very deep recursion over long linear data is better written as a loop.

## Overlapping subproblems and memoisation

Naive Fibonacci recomputes the same values exponentially many times:

```python
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)    # fib(35) takes seconds
```

Cache each result once and it becomes linear:

```python
from functools import cache

@cache
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)    # fib(300) is instant
```

This "recursion plus a cache" is the heart of **dynamic programming**.

## Big-O in one paragraph

Big-O describes how work grows with input size `n`, ignoring constants.
`O(1)` does not grow (dict lookup). `O(log n)` grows by one step each time `n`
doubles (binary search). `O(n)` touches each item once (a loop). `O(n log n)`
is good sorting. `O(n²)` is a loop inside a loop over the same data, and is
where "works on my test data" turns into "hangs in production".

Membership: `x in some_list` is `O(n)`; `x in some_set` is `O(1)`. Converting a
list to a set before many lookups is one of the most common easy speedups.

## Binary search

On **sorted** data, compare with the middle and discard half each step:

```python
def contains(items, target):
    lo, hi = 0, len(items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if items[mid] == target:
            return True
        if items[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False
```

A million items take at most 20 steps. The standard library version is `bisect`.

## Generating combinations

Recursion is the natural way to build every arrangement: pick a first
element, then recurse on the rest. (`itertools.permutations` exists; writing
it once teaches the pattern behind backtracking search.)

## Your turn

In `algorithms.py`:

- `flatten(nested)`: flatten arbitrarily nested lists: `[1, [2, [3, []]]]` gives `[1, 2, 3]`
- `binary_search(items, target)`: the index of `target` in the sorted list, or
  `-1`. Write the loop yourself (no `bisect`, no `.index`).
- `permutations(items)`: a list of every ordering of the list, as lists, in the
  order produced by picking each position's item left to right
- `count_paths(rows, cols)`: how many ways to go from the top-left to the
  bottom-right of a grid moving only right or down. Must be fast for 30 by 30.
