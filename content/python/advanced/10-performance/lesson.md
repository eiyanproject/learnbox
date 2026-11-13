---
title: Performance
summary: Measure before optimising, find the hot spot with cProfile, and fix it with the right data structure or algorithm.
order: 10
files: [fast.py]
run: python -m cProfile -s cumtime fast.py
hints:
  - "`common_items`: `set(b)` once, then keep items of `a` that are in it. Keep order and drop duplicates with a second `seen` set."
  - "`has_pair_with_sum`: walk once, keeping a set of seen numbers; for each `x`, check whether `target - x` is already in it."
  - "`word_frequencies`: `collections.Counter(text.split())` replaces the repeated `.count()` calls."
  - "`build_report`: collect the pieces in a list and `\"\".join(...)` once, instead of `+=` on a growing string."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **optimising** | changing code so it runs faster or uses less memory |
| **hot spot** | the small part of a program where most of the time goes |
| **benchmark** | timing a piece of code, usually many runs to smooth out noise |
| **profiler** | a tool that records every function call while a program runs and reports the time in each |
| **`ncalls`** | how many times a function was called |
| **`tottime`** | time in the function's own code, excluding the functions it called |
| **`cumtime`** (cumulative) | time in the function including everything it called |
| **algorithmic win** | a better algorithm or data structure, such as `O(n²)` to `O(n)` |
| **Big-O** | how the work grows with the input size (the Recursion lesson) |
| **hidden inner loop** | an operation that looks like one step but goes through a whole collection, such as `x in some_list` |
| **constant factor** | how fast each step is, which matters only after the algorithm is right |
| **interpreter** | the program that runs Python code; built-ins run their loops in C inside it |
| **pure function** | one whose result depends only on its arguments, so caching it is safe |
| **compiled extension** | a module written in a compiled language such as C or Rust (with PyO3) |
| **CPU-bound** | limited by computation rather than waiting |

### Python tools and functions

| Name | What it does |
|---|---|
| `timeit.timeit(stmt, setup=..., number=n)` | runs the statement `n` times and returns the total seconds; `setup` runs once first; `stmt` may be a string or a function |
| `set(b)` | build once for fast membership tests |
| `collections.Counter(words)` | counts every item in one pass |
| `"".join(pieces)` | joins strings once, instead of `+=` in a loop |
| `collections.deque` | fast adds and removals at the front |
| `min(...)` | the minimum without sorting |
| `functools.cache` | remembers results of a pure function |
| `append = out.append` | looks a method up once outside a hot loop |
| `numpy` | a third-party library for fast number crunching over whole arrays |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python -m cProfile -s cumtime fast.py` | runs `fast.py` under the profiler, sorted by cumulative time |
| `python -m timeit "statement"` | times a statement, choosing the number of runs for you |

---

A program that is fast enough needs no optimising, and most code is fast
enough. When something really is too slow, the instinct is to start
rewriting the part that *looks* slow. That instinct is usually wrong. This
lesson is about the reliable way: measure to find the real hot spot, then fix
it, usually by changing the algorithm or the data structure rather than by
fiddling with small details.

## Measure first

Guessing where time goes is usually wrong, even for experienced
programmers. Measure.

For a small piece of code, `timeit` runs it many times and reports the total
seconds, which smooths out the noise of a single run:

```pycon
>>> import timeit
>>> seconds = timeit.timeit("sum(range(1000))", number=10_000)
>>> seconds < 5                # the exact time depends on the machine
True
```

`number=10_000` runs the statement ten thousand times; divide by it for the
time of one run. Comparing two ways of doing the same job is where `timeit`
shines. Here is a membership test on a list against the same test on a set:

```pycon
>>> setup = "items = list(range(10_000)); as_set = set(items)"
>>> in_list = timeit.timeit("9_999 in items", setup=setup, number=1_000)
>>> in_set = timeit.timeit("9_999 in as_set", setup=setup, number=1_000)
>>> in_set < in_list           # usually hundreds of times faster
True
```

(`setup` runs once, before the timing starts, so building the data is not
counted.) In the terminal, the same tool is
`python -m timeit "'-'.join(map(str, range(100)))"`, which picks a sensible
number of runs for you and prints the time per run.

For whole programs, **profile** to find where the time is spent. A profiler
records every function call while the program runs, then reports how much
time went into each:

```console
$ python -m cProfile -s cumtime fast.py
```

This lesson's **Run** button runs exactly that. The output is a table, one
row per function, along these lines (trimmed, and the numbers will differ):

```text
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.006    0.006    2.351    2.351 fast.py:1(<module>)
        1    1.831    1.831    1.832    1.832 fast.py:9(has_pair_with_sum)
        1    0.421    0.421    0.422    0.422 fast.py:1(common_items)
        1    0.001    0.001    0.057    0.057 fast.py:17(word_frequencies)
      500    0.056    0.000    0.056    0.000 {method 'count' of 'list' objects}
        1    0.003    0.003    0.005    0.005 fast.py:26(build_report)
```

- `ncalls` is how many times the function was called.
- `tottime` is the time spent in the function's own code, *excluding* the
  functions it called.
- `cumtime` (cumulative) is the time spent in the function *including*
  everything it called.
- `-s cumtime` sorts the table by `cumtime`, so the biggest costs are at the
  top.

Look at the few functions at the top: they are where the time goes, and
optimising anything else is wasted effort. In the sample, `has_pair_with_sum`
takes most of the 2.35 seconds, so it is the one to fix first; `build_report`
takes almost nothing at this size, so rewriting it first would barely help.
`word_frequencies` shows the difference between the two time columns: its
`tottime` is tiny but its `cumtime` is not, because its time is really spent
in the 500 calls to `list.count` it makes.

## The big wins are algorithmic

A 10% faster loop does not rescue an `O(n²)` algorithm (the Big-O notation
from the Recursion lesson). Doubling the input of an `O(n²)` function makes
it four times slower however tight its loop is, while an `O(n)` version only
gets twice as slow. On large inputs, the algorithm decides everything.

The classic Python traps all come from **hidden inner loops**: an operation
that looks like a single step but secretly goes through a whole collection.
Inside a loop, that turns `O(n)` into `O(n²)`:

| Slow | Why | Fast |
|---|---|---|
| `x in some_list` inside a loop | each `in` scans the list | build a `set` once |
| `list.count(x)` for every x | scans the list per item | `Counter` |
| `s += piece` in a loop | may copy the whole string each time (CPython often optimises this, other Pythons do not) | `"".join(pieces)` |
| `lst.pop(0)` / `insert(0, x)` | shifts every item | `collections.deque` |
| `sorted(...)[0]` for the minimum | sorts everything | `min(...)` |
| re-computing the same value | repeated work | cache it |

Strings cannot change, so `s = s + piece` builds a brand new string and
copies everything so far into it, every time round. Joining a list of pieces
once at the end copies each character only once.

The fix for a membership trap, in full:

```pycon
>>> def slow_common(a, b):
...     return [x for x in a if x in b]          # `in b` scans b every time
...
>>> def fast_common(a, b):
...     b_set = set(b)                           # build the set once: O(len(b))
...     return [x for x in a if x in b_set]      # each lookup is O(1)
...
>>> a, b = list(range(5_000)), list(range(2_500, 7_500))
>>> slow_common(a, b) == fast_common(a, b)       # same result...
True
>>> t_slow = timeit.timeit(lambda: slow_common(a, b), number=1)
>>> t_fast = timeit.timeit(lambda: fast_common(a, b), number=1)
>>> t_fast * 20 < t_slow                         # ...far less time
True
```

(`timeit` also accepts a function with no arguments instead of a string,
which is why the calls are wrapped in `lambda`.)

## Cheaper Python

After the algorithm is right, some constant-factor tips. Each one makes the
same work a bit cheaper, and is only worth it in code the profiler has shown
to be hot:

- Built-ins and comprehensions run their loops in C, inside the interpreter,
  and beat hand-written Python loops: `sum(xs)` beats a `for` loop with
  `total += x`.
- Look attributes up once outside a hot loop: `append = out.append`, then
  call `append(x)` inside. Every `out.append` is a lookup, and in a loop of
  millions they add up.
- Generators avoid building huge intermediate lists that are thrown away
  immediately.
- `__slots__` shrinks many small objects (the Descriptors lesson).
- `functools.cache` removes repeated pure computations. ("Pure" means the
  result depends only on the arguments, so caching it is safe.)

And when Python itself is the bottleneck: `numpy` for number crunching (its
operations run over whole arrays in compiled code), multiprocessing for
CPU-bound parallel work (Pro section), or moving the hot loop into a compiled
extension (Rust with PyO3 is a popular choice).

## Your turn

`fast.py` works, but every function is quadratic or worse. Keep the results
**exactly** the same, including order, and make each one fast on large
inputs. The tests time each function on inputs where the slow versions take
seconds, and allow half a second.

- `common_items(a, b)`: the items of `a` that are also in `b`, in the order
  they first appear in `a`, with no duplicates:
  `common_items([3, 1, 3, 2, 5], [5, 3, 9, 3])` is `[3, 5]`.
- `has_pair_with_sum(nums, target)`: are there two different positions whose
  values add up to `target`? `[5, 5]` with target 10 is `True` (two different
  positions, even though the values are equal); `[5]` with target 10 is
  `False` (one 5 cannot be used twice).
- `word_frequencies(text)`: a dict of word to count, with keys in the order
  each word first appears: `"b a b c a b"` gives `{"b": 3, "a": 2, "c": 1}`.
  (A `Counter` keeps first-appearance order too, but the result should be a
  dict with those keys and counts.)
- `build_report(rows)`: one line `"<name>: <value>\n"` per `(name, value)`
  row, all joined into one string; no rows gives `""`.

Press **Run** first to see the profile of the slow version, then again after
each fix to watch that function drop down the table.
