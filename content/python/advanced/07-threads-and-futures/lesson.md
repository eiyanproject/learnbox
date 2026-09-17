---
title: Threads and futures
summary: Run I/O-bound work concurrently with ThreadPoolExecutor, protect shared state with locks, and hand work over queues.
order: 7
files: [concurrent_tools.py]
run: python -i concurrent_tools.py
hints:
  - "`fetch_all(urls, fetch, max_workers)`: `with ThreadPoolExecutor(max_workers) as pool: return list(pool.map(fetch, urls))`. `map` keeps the input order."
  - "`Counter.increment` must hold the lock across read-modify-write: `with self._lock: self.value += 1`."
  - "`first_success`: submit everything, then loop over `as_completed(futures)`; return the first `future.result()` that does not raise. If all fail, raise `RuntimeError`."
  - "`worker_pipeline`: start `n_workers` threads that `while (item := q.get()) is not None: out.append(process(item))`. Put every job, then one `None` per worker, then `join()` the threads."
---

## Concurrency, parallelism and the GIL

CPython has a **Global Interpreter Lock**: only one thread executes Python
bytecode at a time. So threads do **not** make CPU-heavy Python code faster.
They are excellent for **I/O-bound** work, because a thread waiting on the
network, a disk or `time.sleep` releases the GIL and lets others run.

- Many slow network calls or file operations: threads (or asyncio)
- Heavy computation in Python: processes (see the Pro track)

(Python 3.13 ships an experimental free-threaded build without the GIL; the
patterns below stay correct either way.)

## ThreadPoolExecutor

You almost never need to manage `threading.Thread` objects yourself:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=8) as pool:
    pages = list(pool.map(download, urls))      # results in input order
```

Leaving the `with` block waits for all work to finish.

## Futures

`submit` schedules one call and returns a `Future`, a handle to a result that
does not exist yet:

```python
from concurrent.futures import as_completed

with ThreadPoolExecutor() as pool:
    futures = {pool.submit(download, u): u for u in urls}
    for fut in as_completed(futures):           # in completion order
        url = futures[fut]
        try:
            page = fut.result()                 # re-raises the worker's exception
        except OSError as e:
            print(url, "failed:", e)
```

`future.result(timeout=5)`, `future.done()` and `future.cancel()` round out the API.

## Race conditions

`count += 1` is several steps: read, add, write. Two threads can both read 5
and both write 6. The fix is a **lock** around the whole read-modify-write:

```python
import threading

lock = threading.Lock()
with lock:
    count += 1
```

Hold locks briefly, never do I/O while holding one if you can avoid it, and
always acquire multiple locks in the same order everywhere, or two threads can
wait on each other forever (deadlock).

## Queues

`queue.Queue` is thread-safe. It is the simplest correct way to pass work
between threads: producers `put`, workers `get`. A special value (a
**sentinel**, often `None`) tells a worker to stop:

```python
import queue, threading

q = queue.Queue()

def worker():
    while (job := q.get()) is not None:
        handle(job)

threads = [threading.Thread(target=worker) for _ in range(4)]
for t in threads: t.start()
for job in jobs: q.put(job)
for _ in threads: q.put(None)       # one stop signal per worker
for t in threads: t.join()
```

## Your turn

In `concurrent_tools.py`:

- `fetch_all(urls, fetch, max_workers=8)`: call `fetch(url)` for every url
  concurrently and return the results in input order. The tests use a `fetch`
  that sleeps, so doing it one after another is too slow.
- `Counter`: thread-safe `increment()` and a `value` attribute
- `first_success(funcs)`: run the zero-argument functions concurrently and
  return the first result that did not raise; if all raise, raise `RuntimeError`
- `worker_pipeline(items, process, n_workers)`: process all items with
  `n_workers` threads fed from a `queue.Queue` stopped with sentinels; return
  the **sorted** results
