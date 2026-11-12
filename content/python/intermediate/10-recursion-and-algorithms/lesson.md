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

Some problems are easiest to describe in terms of a smaller version of
themselves. "The total size of a folder is the size of its files plus the
total size of each folder inside it." "The factorial of 5 is 5 times the
factorial of 4." This lesson turns that way of thinking into code, then
looks at how to judge whether code will stay fast as its input grows, and
at the classic technique that makes searching sorted data almost free.

## Recursion

A **recursive** function solves a problem by calling itself on a smaller
version of it. Every recursive function needs:

1. a **base case** that answers directly, without calling itself, and
2. a **recursive case** that calls itself on a smaller input, so that every
   chain of calls eventually reaches the base case.

```pycon
>>> def factorial(n):
...     if n <= 1:              # base case
...         return 1
...     return n * factorial(n - 1)
...
>>> factorial(5)
120
```

The factorial of `n` is `1 * 2 * ... * n`. To see how the function gets
there, follow the calls. Each call waits for the one it made to return:

```text
factorial(5) = 5 * factorial(4)
                   factorial(4) = 4 * factorial(3)
                                      factorial(3) = 3 * factorial(2)
                                                         factorial(2) = 2 * factorial(1)
                                                                            factorial(1) = 1   <- base case
                                                         factorial(2) = 2 * 1 = 2
                                      factorial(3) = 3 * 2 = 6
                   factorial(4) = 4 * 6 = 24
factorial(5) = 5 * 24 = 120
```

The calls go down until `n` reaches 1, which answers directly. Then the
answers come back up, each call finishing its multiplication with the result
it was waiting for. Every waiting call is kept in memory as a **frame**
(its own local variables and where it had got to), and there are five frames
at the deepest point.

The two rules matter. Without a base case, or with a recursive case that
does not get smaller, the calls never stop.

Recursion fits naturally on data that is itself recursive: nested lists,
trees, file systems, expressions. A list that may contain lists is either an
ordinary item or a smaller nested list, so a function over it calls itself
for each inner list:

```pycon
>>> def nested_sum(items):
...     total = 0
...     for item in items:
...         if isinstance(item, list):
...             total += nested_sum(item)   # a smaller nested list
...         else:
...             total += item               # an ordinary number
...     return total
...
>>> nested_sum([1, [2, 3], [4, [5]]])
15
```

`isinstance(item, list)` asks "is this a list?". A folder is the same shape,
so this one-liner adds up the size of everything under a folder, however
deep (a fragment: `folder` is a `Path`, from the Files lesson):

```python
def total_size(folder):
    return sum(total_size(x) if x.is_dir() else x.stat().st_size for x in folder.iterdir())
```

Python limits how deep recursion can go, to about 1000 frames by default
(`sys.getrecursionlimit()` gives the exact number). Going past it raises
`RecursionError`, which is also what a missing base case looks like:

```pycon
>>> def forever(n):
...     return forever(n + 1)       # no base case
...
>>> forever(0)
Traceback (most recent call last):
  ...
RecursionError: maximum recursion depth exceeded...
```

So very deep recursion over long linear data, such as walking a list of a
million items one call per item, is better written as a loop. Recursion
shines when each call splits the problem, so the depth stays small.

## Overlapping subproblems and memoisation

The Fibonacci numbers are 0, 1, 1, 2, 3, 5, 8, ..., each the sum of the two
before it. The definition translates directly into code, but this naive
version recomputes the same values exponentially many times:

```python
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)    # fib(35) takes seconds
```

`fib(5)` calls `fib(4)` and `fib(3)`. But `fib(4)` *also* calls `fib(3)`, and
each `fib(3)` calls `fib(2)` again, and so on. Counting the calls shows how
fast that grows:

```pycon
>>> calls = 0
>>> def fib(n):
...     global calls
...     calls += 1
...     return n if n < 2 else fib(n - 1) + fib(n - 2)
...
>>> fib(20)
6765
>>> calls
21891
```

Almost 22,000 calls to work out 21 different values. Each step up in `n`
multiplies the work by about 1.6, so `fib(35)` makes about 30 million calls.
(`global` is used here only to count; as the Scope lesson said, avoid it in
real code.)

The fix is to remember each result the first time it is worked out, and
reuse it after that, which is **memoisation** (you wrote a `memoize`
decorator in the Decorators lesson). `functools.cache` is the ready-made
version. Cache each result once and it becomes linear:

```pycon
>>> from functools import cache
>>> calls = 0
>>> @cache
... def fib(n):
...     global calls
...     calls += 1
...     return n if n < 2 else fib(n - 1) + fib(n - 2)
...
>>> fib(20)
6765
>>> calls                   # each value from 0 to 20 worked out once
21
>>> fib(300)                # instant
222232244629420445529739893461909967206666939096499764990979600
```

This "recursion plus a cache" is the heart of **dynamic programming**: when
a problem breaks into subproblems that overlap, solve each one once and
store the answer. This lesson's `count_paths` exercise is one.

## Big-O in one paragraph

**Big-O** notation describes how the work a piece of code does grows as its
input size `n` grows. It ignores constant factors (whether each step takes
one nanosecond or ten), because for large inputs the *shape* of the growth is
what decides whether code finishes:

| Big-O | Name | What happens when `n` doubles | Example |
|---|---|---|---|
| `O(1)` | constant | no change | a dict lookup |
| `O(log n)` | logarithmic | one more step | binary search |
| `O(n)` | linear | twice the work | a loop over the items |
| `O(n log n)` | | a bit more than twice | good sorting, such as `sorted()` |
| `O(n²)` | quadratic | four times the work | a loop inside a loop over the same data |

`O(n²)` is where "works on my test data" turns into "hangs in production": a
loop that takes 1 ms on 100 items takes 100 seconds on 100,000 items.

A common, quiet case is membership tests. `x in some_list` is `O(n)`, since
it checks the items one by one; `x in some_set` is `O(1)`, like a dict
lookup. Testing each of `n` items against a list of `n` items is therefore
`O(n²)`. Converting the list to a set once, before many lookups, makes it
`O(n)`, and is one of the most common cheap speed-ups there is.

## Binary search

Looking for a word in a dictionary, you do not start at page one. You open it
in the middle, see whether the word comes before or after that page, and
repeat on the half that must contain it. **Binary search** does the same on
**sorted** data: compare with the middle item, and discard the half that
cannot hold the target, each step:

```pycon
>>> def contains(items, target):
...     lo, hi = 0, len(items) - 1
...     while lo <= hi:
...         mid = (lo + hi) // 2
...         if items[mid] == target:
...             return True
...         if items[mid] < target:
...             lo = mid + 1
...         else:
...             hi = mid - 1
...     return False
...
>>> contains([2, 5, 8, 11, 14, 17], 14)
True
>>> contains([2, 5, 8, 11, 14, 17], 6)
False
```

`lo` and `hi` are the first and last positions still in play. Looking for 14:

1. `lo` is 0 and `hi` is 5, so `mid` is 2, and `items[2]` is 8. 8 is less
   than 14, so 14 can only be to the right: `lo` becomes 3.
2. `lo` is 3, `hi` is 5, `mid` is 4, and `items[4]` is 14. Found.

For 6, the range shrinks until `lo` passes `hi`, meaning there is nowhere
left to look, and the loop ends with `False`. Moving the bound *past* `mid`
(`mid + 1`, `mid - 1`) matters: `mid` has already been checked, and leaving
it in the range can make the loop run forever.

Each step halves what is left, so a million items take at most 20 steps.
The standard library version is `bisect`, from the collections lesson. It
only works because the data is sorted; on unsorted data, discarding half is
not safe.

## Generating combinations

Recursion is the natural way to build every arrangement of some items: pick a
first item, then recurse to arrange the rest, and repeat for each possible
first item. For `[1, 2, 3]`: take 1 first and arrange `[2, 3]` (giving
`[1, 2, 3]` and `[1, 3, 2]`), then take 2 first and arrange `[1, 3]`, then 3
first and arrange `[1, 2]`. Arranging a list of one item, or of none, is the
base case: there is only one way.

The number of arrangements grows fast: `n` items have `n!` (n factorial)
orderings, so 10 items already have 3,628,800. (`itertools.permutations`
exists; writing it once teaches the pattern behind **backtracking** search,
which tries choices one at a time and undoes them to try the next.)

## Your turn

In `algorithms.py`:

- `flatten(nested)`: flatten arbitrarily nested lists into one flat list, in
  order: `[1, [2, [3, []]]]` gives `[1, 2, 3]`, and `[]` gives `[]`.
- `binary_search(items, target)`: the index of `target` in the sorted list, or
  `-1` if it is not there: `binary_search([2, 5, 8, 11], 8)` is `2`, and
  searching an empty list gives `-1`. Write the loop yourself: a test reads
  your file and fails if the word `bisect` or the text `.index(` appears
  anywhere in it, comments included. Another test times it on two million
  items, so it must really halve the range each step.
- `permutations(items)`: a list of every ordering of the list, each one a
  list. Build them by choosing the first item, then every ordering of the
  rest, taking choices from left to right, which gives this order:
  `permutations([1, 2, 3])` is
  `[[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]`.
  The empty list has exactly one ordering, the empty one, so
  `permutations([])` is `[[]]`.
- `count_paths(rows, cols)`: picture a grid of `rows` by `cols` squares. You
  start in the top-left square and want to reach the bottom-right one, and
  each move goes one square right or one square down. Return how many
  different routes there are. `count_paths(2, 2)` is `2` (right then down, or
  down then right), `count_paths(3, 3)` is `6`, and a single row or column
  has only one route. Think about the last move: every route arrives either
  from the square above or from the square to the left. It must finish
  30 by 30 in under a second, so the overlapping subproblems need caching.
