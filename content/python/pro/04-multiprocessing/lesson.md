---
title: Multiprocessing
summary: Use every CPU core for CPU-bound work with ProcessPoolExecutor, chunk work sensibly, and know what can cross a process boundary.
order: 4
files: [parallel.py]
run: python parallel.py
hints:
  - "Worker functions must be defined at module top level so they can be pickled. `count_primes_in_range(bounds)` takes a `(start, stop)` tuple."
  - "`split_range(start, stop, parts)`: `step = ceil((stop - start) / parts)`; build `(lo, min(lo + step, stop))` for `lo in range(start, stop, step)`."
  - "`parallel_prime_count`: `with ProcessPoolExecutor(max_workers=workers) as pool: return sum(pool.map(count_primes_in_range, split_range(...)))`."
  - "`map_with_errors`: submit each item, then for each future `try: results.append((\"ok\", fut.result()))` / `except Exception as e: results.append((\"error\", type(e).__name__))`, keeping input order."
---

The Threads lesson made waiting overlap. It could not make *computing*
faster: counting the primes below ten million on four threads takes as long
as on one, because of the GIL. Most computers have several CPU cores, though,
and pure computation could use all of them at once. This lesson shows how,
with **processes**, and what you have to give up to get it.

## Why processes

A **process** is a running program with its own memory. Threads share one
interpreter and, in standard CPython, one GIL: only one of them runs Python
code at a time, so pure-Python computation does not get faster with threads.
Processes each have their own interpreter and their own GIL, so CPU-bound
work (work limited by calculation speed, not by waiting) really runs in
parallel, one process per core.

The cost: processes do not share memory. A worker process cannot see your
variables, so every argument has to be sent to it and every result sent
back. To send a Python object to another process, it is **pickled**:
converted into bytes by the `pickle` module, sent across, and **unpickled**
back into an equal object on the other side. That overhead is real, and it
decides how to split the work.

```pycon
>>> import pickle
>>> data = pickle.dumps({"range": (0, 100)})    # object -> bytes
>>> type(data)
<class 'bytes'>
>>> pickle.loads(data)                           # bytes -> an equal object
{'range': (0, 100)}
```

## ProcessPoolExecutor

`ProcessPoolExecutor` has the same interface as `ThreadPoolExecutor` from
the Threads lesson (`map`, `submit`, futures), but each worker is a separate
process:

```python
from concurrent.futures import ProcessPoolExecutor

def crunch(n):                       # top-level function: picklable
    return sum(i * i for i in range(n))

if __name__ == "__main__":
    with ProcessPoolExecutor() as pool:            # defaults to os.cpu_count() workers
        results = list(pool.map(crunch, [10**6] * 8))
```

This sends the number `10**6` to a worker eight times (spread over the pool's
processes), each worker computes `crunch` on its own core, and the eight
results come back in input order. With four cores it takes about a quarter
of the time the eight calls would take in a row. `os.cpu_count()` is the
number of cores the machine reports.

(This block is a script, not something to paste into the `>>>` prompt:
process pools need the function to live in an importable file, as the next
section explains.)

## Rules that bite

- **The `__main__` guard is mandatory** on platforms that start workers by
  importing your module fresh: "spawn", the default on macOS and Windows,
  and "forkserver", the Linux default from Python 3.14 (earlier versions on
  Linux use "fork", which copies the running process instead, but the guard
  is still the portable habit). Each worker imports your file to find the
  worker function. Without the guard, that import would run the pool-creating
  code again, and each worker would try to start its own pool.
- **Only picklable things cross.** Functions are pickled *by name*: the
  worker receives "the function `crunch` in module `parallel`" and looks it
  up by importing that module. So worker functions must live at module top
  level, where they can be found by name. Lambdas and nested functions have
  no importable name, and open files, sockets and locks are tied to the
  process they were opened in; none of these can be sent.
- **Workers do not see your later changes to globals.** Each worker has its
  own copy of the module's memory. Pass everything a task needs as
  arguments.
- **Exceptions come back** through `future.result()`, like with threads: the
  exception is pickled in the worker and raised again in the parent.

The pickling rule is easy to check without any pool:

```pycon
>>> pickle.dumps(lambda x: x * 2)
Traceback (most recent call last):
  ...
_pickle.PicklingError: Can't pickle <function <lambda> at 0x...>: ...
```

(The exact message varies between Python versions, but a lambda can never
be pickled.)

## Chunking

Sending a task costs a pickle on the way out and another on the way back.
If each task is tiny, say "is 7 prime?", the sending costs more than the
work, and a million tiny tasks spend nearly all their time pickling. Send a
few large chunks instead, roughly one or a few per worker: "count the primes
from 0 to 250,000", "from 250,000 to 500,000", and so on. Each chunk is one
message out and one number back.

Splitting a range into chunks is simple arithmetic:

```pycon
>>> def split(start, stop, parts):
...     step = -(-(stop - start) // parts)       # ceiling division
...     return [(lo, min(lo + step, stop)) for lo in range(start, stop, step)]
...
>>> split(0, 10, 3)        # the last chunk takes what is left
[(0, 4), (4, 8), (8, 10)]
```

`-(-a // b)` is a common trick for dividing and rounding **up**: `//` rounds
down, and doing it on the negated number rounds the other way. 10 values in 3
parts gives chunks of 4 (3.33 rounded up), so the chunks start at 0, 4 and 8,
and `min(lo + step, stop)` stops the last one at 10 instead of 12.

`pool.map(func, items, chunksize=500)` does the same batching for you when
the items are individually small: it sends them 500 at a time instead of one
by one.

## When it is not worth it

- **Short jobs.** Starting worker processes takes time (tens of milliseconds
  each), and so does pickling. A job that takes a tenth of a second in one
  process will be slower with a pool.
- **Work that is mostly I/O.** Waiting does not need extra cores; threads or
  asyncio are much lighter.
- **Data too large to copy cheaply.** Sending a gigabyte array to each worker
  means pickling a gigabyte each time. `multiprocessing.shared_memory` or
  memory-mapped files let processes share one copy instead.

In this LXC, all learner processes share a memory and process-count limit, so
a pool of a few workers is plenty.

## Your turn

In `parallel.py`:

- `is_prime(n)`: `True` for prime numbers. 0 and 1 are not prime; 2 is.
  Trying divisors up to the square root of `n` is enough: if `n` has a factor
  larger than its square root, it also has one smaller.
- `count_primes_in_range(bounds)`: takes a **single** `(start, stop)` tuple
  (one argument, so it can be passed straight to `pool.map`) and counts the
  primes in `range(start, stop)`: `count_primes_in_range((0, 10))` is `4`
  (2, 3, 5 and 7), and an empty range gives `0`.
- `split_range(start, stop, parts)`: cut `range(start, stop)` into
  consecutive `(lo, hi)` chunks, each meaning `range(lo, hi)`, that together
  cover it exactly, with no gaps or overlaps. Every chunk holds the same
  number of values - the length of the range divided by `parts`, **rounded
  up** - except the last, which holds what is left. That gives at most
  `parts` chunks, and never an empty one:
  - `split_range(0, 10, 3)` is `[(0, 4), (4, 8), (8, 10)]` (chunks of 4)
  - `split_range(10, 13, 8)` is `[(10, 11), (11, 12), (12, 13)]` (only three
    values, so three chunks of 1)
  - `split_range(0, 0, 4)` is `[]`
- `parallel_prime_count(start, stop, workers=2)`: count the primes in
  `range(start, stop)` by splitting it into chunks and counting each chunk
  in a `ProcessPoolExecutor` with `workers` processes. The answer must match
  the single-process count exactly.
- `map_with_errors(func, items, workers=2)`: run `func` on each item in a
  process pool. Return a list in input order with one tuple per item:
  `("ok", result)` if the call returned, or `("error", "<ExceptionClassName>")`
  if it raised, such as `("error", "ZeroDivisionError")`. One failing item
  must not stop the others. The tests pass functions from a separate helper
  module, since a function defined inside a test could not be pickled.
