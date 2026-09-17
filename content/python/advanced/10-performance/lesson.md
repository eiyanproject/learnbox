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

## Measure first

Guessing where time goes is usually wrong. Measure:

```python
import timeit
timeit.timeit("sum(range(1000))", number=10_000)
```

In the terminal: `python -m timeit "'-'.join(map(str, range(100)))"`.

For whole programs, **profile** to find where the time is spent:

```console
$ python -m cProfile -s cumtime fast.py
```

`cumtime` is time spent in a function including everything it calls; `tottime`
excludes the calls. Look for the few functions at the top: optimising anything
else is wasted effort.

## The big wins are algorithmic

A 10% faster loop does not rescue an `O(n²)` algorithm. The classic Python
traps all come from hidden inner loops:

| Slow | Why | Fast |
|---|---|---|
| `x in some_list` inside a loop | each `in` scans the list | build a `set` once |
| `list.count(x)` for every x | scans the list per item | `Counter` |
| `s += piece` in a loop | may copy the whole string each time (CPython often optimises this, other Pythons do not) | `"".join(pieces)` |
| `lst.pop(0)` / `insert(0, x)` | shifts every item | `collections.deque` |
| `sorted(...)[0]` for the minimum | sorts everything | `min(...)` |
| re-computing the same value | repeated work | cache it |

## Cheaper Python

After the algorithm is right, some constant-factor tips:

- Built-ins and comprehensions run in C and beat hand-written loops.
- Look attributes up once outside a hot loop (`append = out.append`).
- Generators avoid building huge intermediate lists.
- `__slots__` shrinks many small objects.
- `functools.cache` removes repeated pure computations.

And when Python itself is the bottleneck: `numpy` for number crunching,
multiprocessing for CPU-bound parallel work (Pro track), or moving the hot loop
into a compiled extension (Rust with PyO3 is a popular choice).

## Your turn

`fast.py` works, but every function is quadratic or worse. Keep the results
**exactly** the same and make each one fast on large inputs. The tests time each function on inputs where
the slow versions take seconds.

- `common_items(a, b)`: items of `a` also in `b`, first occurrence order, no duplicates
- `has_pair_with_sum(nums, target)`: are there two different positions whose values add up to `target`?
- `word_frequencies(text)`: dict of word to count, keys in first-appearance order
- `build_report(rows)`: one line `"<name>: <value>\n"` per `(name, value)` row

Run the file with **Run** to see the profile of the slow version first.
