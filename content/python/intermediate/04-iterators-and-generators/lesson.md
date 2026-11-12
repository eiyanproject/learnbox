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

A `for` loop works on lists, strings, dicts, files, ranges and more. This
lesson shows the single mechanism behind all of them, and how to plug your
own code into it. The payoff is **generators**: functions that produce a
sequence of values one at a time, on demand. With them you can process a
log file far bigger than your memory, or work with a sequence that never
ends, using ordinary `for` loops.

## The iterator protocol

A `for` loop works on anything **iterable**: any object that can hand out
its items one after another. Lists, strings, dicts, sets, files and ranges
are all iterable.

The handing out is done by a second kind of object, an **iterator**. You get
one by passing an iterable to `iter()`, and you ask it for the next item with
`next()`. When there are no items left, `next()` raises `StopIteration`.
That rule, and nothing more, is called the **iterator protocol**:

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

A `for` loop does exactly this for you. `for x in items:` works like this:

1. Call `iter(items)` once, to get an iterator.
2. Call `next()` on it, and put the result in `x`.
3. Run the loop body.
4. Go back to step 2. When `next()` raises `StopIteration`, the loop
   catches it and ends quietly.

The difference between the two kinds of object matters. A list is iterable
but is not itself an iterator: you can loop over it as often as you like,
because each loop gets a fresh iterator that starts at the beginning. An
**iterator** remembers its position and hands out one value per `next()`.
Once used up, it stays used up.

`map(function, iterable)` is a built-in that gives you an iterator, which
applies the function to each item as it is asked for one. Being an iterator,
it can only be gone through once:

```pycon
>>> squares = map(lambda x: x * x, [1, 2, 3])
>>> list(squares)
[1, 4, 9]
>>> list(squares)   # already used up
[]
```

The second `list()` gets nothing, and no error either: the iterator is at
its end, so it raises `StopIteration` straight away, and `list()` treats that
as "no items". This catches people out when they loop over the same iterator
twice. If you need the values more than once, store them in a list first.

## Generators

Writing an iterator by hand means writing a class that keeps track of where
it is. A generator gets you the same thing from an ordinary-looking function.

A function containing `yield` anywhere in its body is a **generator
function**. Calling it does not run the body; it returns a **generator**, a
kind of iterator. The body then runs **lazily**, which means only as far as it
must, a piece at a time, as values are asked for:

1. Calling `countdown(3)` creates the generator. None of the body runs yet.
2. The first `next()` runs the body from the top until it reaches a `yield`.
   The value after `yield` is handed out, and the function **pauses** there,
   with all its local variables kept as they are.
3. The next `next()` resumes from exactly that point, straight after the
   `yield`, and runs on to the next `yield`.
4. When the body reaches its end (or a `return`), the generator raises
   `StopIteration`, and any loop over it finishes.

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

`"starting"` was printed by the first `next()`, not by `countdown(3)`: that
is the laziness. `list(g)` then called `next()` until the generator finished,
collecting 2 and 1.

Local variables survive between `yield`s: `n` keeps its value while the
function is paused. That is what makes generators so convenient. The
alternative is a class with `__iter__` and `__next__` methods (the special
methods `iter()` and `next()` call), which has to store its position in
attributes by hand.

## Why lazy matters

A generator produces values only when asked, so it never needs to hold the
whole sequence at once. That lets it handle streams that do not fit in
memory, or that never end at all. This one counts upwards forever:

```pycon
>>> def naturals():
...     n = 1
...     while True:
...         yield n
...         n += 1
...
>>> nums = naturals()
>>> next(nums), next(nums), next(nums)
(1, 2, 3)
```

`while True` would freeze an ordinary function, but here each `yield`
pauses it, so it only runs as far as you ask. Do not call `list(naturals())`,
though: `list` asks for every value, and there is no last one, so it would
run until the computer ran out of memory.

## Generator expressions

A comprehension with **round** brackets is a generator rather than a list. It
builds nothing up front and produces each value as it is asked for:

```python
[n * n for n in range(1_000_000)]     # a list: a million values, all in memory
(n * n for n in range(1_000_000))     # a generator: nothing yet
```

You can see the difference at the prompt. The generator is shown as an
object rather than as values, because it has not worked any out yet:

```pycon
>>> gen = (n * n for n in range(5))
>>> gen
<generator object <genexpr> at 0x...>
>>> list(gen)
[0, 1, 4, 9, 16]
```

(The `0x...` is a memory address, which is different every time.)

Functions that consume a sequence once - `sum`, `any`, `all`, `max`, `min`,
`"".join` - take one directly, and the brackets can be dropped when it is the
only argument:

```pycon
>>> sum(n * n for n in range(1000))
332833500
>>> log = ["INFO start", "ERROR disk full", "INFO stop"]
>>> any(line.startswith("ERROR") for line in log)
True
>>> all(line.startswith("INFO") for line in log)
False
```

`any` is true if at least one value is true, and `all` only if every value
is.

`any` and `all` also **stop early**: `any` returns as soon as something is
true, so on a million-line log that matches on line 3, only three lines are
ever read. With a list comprehension you would have built the whole million
first.

Generators compose into **pipelines**, each stage pulling from the one
before. This is the shape of a real log-processing script (a fragment: it
needs a `huge.log` file to run):

```python
import itertools

lines = open("huge.log")                             # a file is an iterator of lines
errors = (l for l in lines if "ERROR" in l)          # generator expression
fields = (l.split("|") for l in errors)
first_ten = itertools.islice(fields, 10)             # stops reading after 10 matches
```

None of these lines reads anything. They only connect the stages. Work
starts when something asks `first_ten` for a value: it asks `fields`, which
asks `errors`, which reads lines from the file until one contains `ERROR`,
and the single matching line travels back up the chain. After ten matches,
`islice` stops asking, so the rest of the file is never read. However big the
file, only one line is in memory at a time.

The same pipeline works on a list standing in for the file:

```pycon
>>> import itertools
>>> lines = ["ok|1", "ERROR|disk", "ok|2", "ERROR|net", "ERROR|cpu"]
>>> errors = (l for l in lines if "ERROR" in l)
>>> fields = (l.split("|") for l in errors)
>>> list(itertools.islice(fields, 2))
[['ERROR', 'disk'], ['ERROR', 'net']]
```

## yield from

`yield from something` yields every value from another iterable, one by
one, as if you had written `for x in something: yield x`. It is especially
handy when a generator calls itself, as this one does for each nested list:

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

For the inner list `[2, [3, 4]]`, `flatten` calls itself and passes every
value that inner call yields straight on to the outer caller, so the values
come out in order however deep the nesting goes.

## itertools highlights

The `itertools` module is a toolbox of ready-made iterators for common jobs.
Each of these returns an iterator; `list()` shows what it produces. (`import
itertools as it` imports the module under the shorter name `it`.)

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

What each one does:

- `count(start)` counts up forever, and `cycle(items)` repeats its items
  forever. Both are infinite, so they are always paired with something that
  stops, such as `islice`.
- `islice(iterator, n)` takes the first `n` items, like slicing a list with
  `[:n]`, but it works on any iterator, including infinite ones.
- `chain(a, b)` runs through `a` and then `b`, as one sequence.
- `takewhile(test, items)` hands out items while the test passes, and stops
  for good at the first one that fails. The `2` at the end is never reached,
  even though it is below 5.
- `accumulate(items)` gives running totals: 1, then 1 + 2, then 1 + 2 + 3.
- `groupby(items)` gives `(key, run)` pairs, one per run of equal items next
  to each other; `run` is itself an iterator over that run.
- `pairwise(items)` gives each item together with the one after it.
- `product("ab", repeat=2)` gives every combination of two picks from `"ab"`.

`groupby` only groups **neighbouring** equal keys - sort first if equal items
can be apart:

```pycon
>>> [key for key, run in it.groupby("abab")]      # no two equal letters touch
['a', 'b', 'a', 'b']
>>> [key for key, run in it.groupby(sorted("abab"))]
['a', 'b']
```

## Your turn

In `generators.py`, write each of these as a generator function (using
`yield`), except `take`, which returns a list:

- `countdown(n)`: yields `n, n-1, ..., 1`: `countdown(3)` yields `3`, `2`, `1`,
  and `countdown(0)` yields nothing at all
- `read_records(lines)`: for each line, strip the surrounding spaces first.
  Skip the line if it is now blank or starts with `#`; otherwise split it at
  the commas and yield the fields as a list. The lines `"a,b"`, `""`,
  `" # note"` and `" c,d "` yield `["a", "b"]` and then `["c", "d"]`.
  It must be lazy: yield each record as soon as its line has been read, and
  do not read further lines until the next record is asked for. A test feeds
  it a generator that fails if it is read too far.
- `fibonacci()`: an infinite generator `0, 1, 1, 2, 3, 5, ...`, each number
  the sum of the two before it
- `take(n, iterable)`: a **list** of the first `n` items. It must work on
  infinite generators: `take(5, fibonacci())` is `[0, 1, 1, 2, 3]`. That
  rules out turning the whole iterable into a list first, which would never
  finish. If there are fewer than `n` items, return all of them:
  `take(5, [1, 2])` is `[1, 2]`.
- `chunked(iterable, size)`: yields lists of `size` items; the last may be
  shorter: `chunked(range(5), 2)` yields `[0, 1]`, `[2, 3]`, `[4]`. It must
  work on any iterable, including iterators that cannot be sliced or measured
  with `len()`, so collect items as you loop rather than slicing.
