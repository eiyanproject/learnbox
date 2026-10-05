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

```pycon
>>> it = iter([10, 20])     # ask the iterable for an iterator
>>> next(it)
10
>>> next(it)
20
>>> next(it)                # a for loop ends here
Traceback (most recent call last):
  ...
StopIteration
```

An **iterator** remembers its position and hands out one value per `next()`.
Once used up, it stays used up:

```pycon
>>> squares = map(lambda x: x * x, [1, 2, 3])
>>> list(squares)
[1, 4, 9]
>>> list(squares)   # already used up
[]
```

## Generators

A function containing `yield` is a **generator function**. Calling it does not
run the body; it returns a generator, which runs the body lazily, pausing at
each `yield`:

```pycon
>>> def countdown(n):
...     print("starting")
...     while n > 0:
...         yield n
...         n -= 1
...
>>> g = countdown(3)     # nothing printed yet
>>> next(g)              # runs the body as far as the first yield
starting
3
>>> list(g)              # carries on from where it paused
[2, 1]
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

print(list(flatten([1, [2, [3, 4]], 5])))
```

```output
[1, 2, 3, 4, 5]
```

## itertools highlights

Each of these returns an iterator; `list()` shows what it produces.

```pycon
>>> import itertools as it
>>> list(it.islice(it.count(10), 5))    # count(10) goes 10, 11, 12... forever;
[10, 11, 12, 13, 14]
>>> list(it.islice(it.cycle("ab"), 5))  # islice takes the first few of any iterator
['a', 'b', 'a', 'b', 'a']
>>> list(it.chain([1, 2], [3]))
[1, 2, 3]
>>> list(it.takewhile(lambda x: x < 5, [1, 4, 6, 2]))   # stops at the first fail
[1, 4]
>>> list(it.accumulate([1, 2, 3]))      # running totals
[1, 3, 6]
>>> [(key, len(list(run))) for key, run in it.groupby("aaabcc")]
[('a', 3), ('b', 1), ('c', 2)]
>>> list(it.pairwise([1, 2, 3]))
[(1, 2), (2, 3)]
>>> ["".join(p) for p in it.product("ab", repeat=2)]
['aa', 'ab', 'ba', 'bb']
```

`groupby` only groups **neighbouring** equal keys - sort first if equal items
can be apart.

## Your turn

In `generators.py`, all as generators unless stated:

- `countdown(n)`: yields `n, n-1, ..., 1`: `countdown(3)` yields `3`, `2`, `1`
- `read_records(lines)`: for each line, strip the surrounding spaces first.
  Skip the line if it is now blank or starts with `#`; otherwise split it at
  the commas and yield the fields as a list. The lines `"a,b"`, `""`,
  `" # note"` and `" c,d "` yield `["a", "b"]` and then `["c", "d"]`.
- `fibonacci()`: an infinite generator `0, 1, 1, 2, 3, 5, ...`, each number
  the sum of the two before it
- `take(n, iterable)`: a **list** of the first `n` items. It must work on
  infinite generators: `take(5, fibonacci())` is `[0, 1, 1, 2, 3]`.
- `chunked(iterable, size)`: yields lists of `size` items; the last may be
  shorter: `chunked(range(5), 2)` yields `[0, 1]`, `[2, 3]`, `[4]`
