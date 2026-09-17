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

## Why processes

Threads share one interpreter and, in standard CPython, one GIL: pure-Python
computation does not get faster with threads. **Processes** each have their
own interpreter and their own GIL, so CPU-bound work really runs in parallel on
multiple cores.

The cost: processes do not share memory. Arguments and results are **pickled**,
sent to another process, and unpickled. That overhead decides how to split the
work.

## ProcessPoolExecutor

Same interface as `ThreadPoolExecutor`:

```python
from concurrent.futures import ProcessPoolExecutor

def crunch(n):                       # top-level function: picklable
    return sum(i * i for i in range(n))

if __name__ == "__main__":
    with ProcessPoolExecutor() as pool:            # defaults to os.cpu_count() workers
        results = list(pool.map(crunch, [10**6] * 8))
```

## Rules that bite

- **The `__main__` guard is mandatory** on platforms that start workers by
  importing your module fresh (macOS and Windows default to "spawn"). Without it,
  each worker would start its own pool.
- **Only picklable things cross.** Lambdas, nested functions, open files,
  sockets and locks cannot be sent. Worker functions must live at module top level.
- **Workers do not see your later changes to globals.** Pass everything a task
  needs as arguments.
- **Exceptions come back** through `future.result()`, like with threads.

## Chunking

Sending a million tiny tasks spends all the time pickling. Send a few large
chunks instead, roughly one or a few per worker:

```python
def split(start, stop, parts):
    step = -(-(stop - start) // parts)       # ceiling division
    return [(lo, min(lo + step, stop)) for lo in range(start, stop, step)]
```

`pool.map(func, items, chunksize=500)` does the same batching for you when the
items are individually small.

## When it is not worth it

Short jobs (process start-up and pickling dominate), work that is mostly I/O
(threads or asyncio are lighter), and data too large to copy cheaply
(`multiprocessing.shared_memory` or memory-mapped files help there).

In this LXC, all learner processes share a memory and process-count limit, so a
pool of a few workers is plenty.

## Your turn

In `parallel.py`:

- `is_prime(n)` and `count_primes_in_range(bounds)`: count primes in
  `range(start, stop)` for a `(start, stop)` tuple
- `split_range(start, stop, parts)`: split into at most `parts` contiguous
  `(lo, hi)` chunks covering the range exactly
- `parallel_prime_count(start, stop, workers=2)`: count primes using a
  `ProcessPoolExecutor` over the chunks
- `map_with_errors(func, items, workers=2)`: run `func` on each item in a
  process pool; return a list in input order of `("ok", result)` or
  `("error", "<ExceptionClassName>")`
