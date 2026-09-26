---
title: Iterators and generators
summary: The iterator protocol, yield, lazy pipelines, and the itertools toolbox.
order: 4
files: [generators.py]
run: python -i generators.py
hints:
  - "`countdown(n)`: `while n > 0: yield n; n -= 1`."
  - "`read_records(lines)`: loop, `line = line.strip()`, skip `not line or line.startswith(\"#\")`, `yield line.split(\",\")`."
  - "`take(n, iterable)` is `list(itertools.islice(iterable, n))`. `fibonacci()` is an infinite `while True` loop."
  - "`chunked`: keep a list, append each item, and `yield` it (then start a new one) when it reaches `size`. Yield what is left at the end if it is not empty."
---

## The iterator protocol

A `for` loop works on anything **iterable**. Under the hood:

```python
it = iter([10, 20])     # ask the iterable for an iterator
next(it)                # 10
next(it)                # 20
next(it)                # raises StopIteration: the loop ends here
```

An **iterator** remembers its position and hands out one value per `next()`.
Once used up, it stays used up:

```python
squares = map(lambda x: x * x, [1, 2, 3])
list(squares)   # [1, 4, 9]
list(squares)   # []  already consumed
```

## Generators

A function containing `yield` is a **generator function**. Calling it does not
run the body; it returns a generator, which runs the body lazily, pausing at
each `yield`:

```python
def countdown(n):
    print("starting")
    while n > 0:
        yield n
        n -= 1

g = countdown(3)     # nothing printed yet
next(g)              # prints "starting", returns 3
list(g)              # [2, 1]
```

Local variables survive between `yield`s. That is what makes generators so
convenient compared with writing a class with `__iter__` and `__next__`.

## Why lazy matters

A generator produces values only when asked, so it can handle streams that do
not fit in memory, or are infinite:

```python
def naturals():
    n = 1
    while True:
        yield n
        n += 1
```

## Generator expressions

A comprehension with **round** brackets is a generator rather than a list. It
builds nothing up front and produces each value as it is asked for:

```python
[n * n for n in range(1_000_000)]     # a list: a million values, all in memory
(n * n for n in range(1_000_000))     # a generator: nothing yet
```

Functions that consume a sequence once - `sum`, `any`, `all`, `max`, `min`,
`"".join` - take one directly, and the brackets can be dropped when it is the
only argument:

```python
sum(n * n for n in range(1000))
any(line.startswith("ERROR") for line in log)
```

`any` and `all` also **stop early**: `any` returns as soon as something is
true, so on a million-line log that matches on line 3, only three lines are
ever read. With a list comprehension you would have built the whole million
first.

Generators compose into **pipelines**, each stage pulling from the one before:

```python
lines = open("huge.log")
errors = (l for l in lines if "ERROR" in l)          # generator expression
fields = (l.split("|") for l in errors)
first_ten = itertools.islice(fields, 10)             # stops reading after 10 matches
```

## yield from

Delegate to another iterable:

```python
def flatten(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item
```

## itertools highlights

```python
import itertools as it

it.islice(gen, 5)                 # first 5 items of any iterator
it.count(10)                      # 10, 11, 12, ... forever
it.cycle("ab")                    # a, b, a, b, ...
it.chain([1, 2], [3])             # 1, 2, 3
it.takewhile(lambda x: x < 5, xs)
it.accumulate([1, 2, 3])          # 1, 3, 6
it.groupby(sorted_items, key=f)   # runs of equal keys (sort first!)
it.pairwise([1, 2, 3])            # (1, 2), (2, 3)
it.product("ab", repeat=2)        # aa, ab, ba, bb
```

## Your turn

In `generators.py`, all as generators unless stated:

- `countdown(n)`: yields `n, n-1, ..., 1`
- `read_records(lines)`: for each line, skip blank lines and lines starting
  with `#`, and yield the comma-separated fields as a list (strip the line first)
- `fibonacci()`: an infinite generator `0, 1, 1, 2, 3, 5, ...`
- `take(n, iterable)`: a **list** of the first `n` items; must work on infinite generators
- `chunked(iterable, size)`: yields lists of `size` items; the last may be shorter
