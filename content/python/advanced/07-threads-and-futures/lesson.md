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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **thread** | a separate line of execution in one program, sharing its memory with the others |
| **concurrency** | several tasks in progress at once, taking turns |
| **parallelism** | several tasks running at the same instant on different CPU cores |
| **CPU core** | one processing unit; a computer usually has several |
| **CPython** | the standard Python implementation |
| **bytecode** | the low-level instructions Python compiles code into and runs |
| **GIL** (Global Interpreter Lock) | lets only one thread run Python bytecode at a time; released while waiting |
| **I/O-bound** | work that mostly waits on something outside the program: network, disk |
| **CPU-bound** | work that mostly computes; threads do not speed it up (processes do) |
| **free-threaded build** | an experimental Python 3.13 build without the GIL |
| **thread pool** | a fixed number of worker threads that run the calls you hand them |
| **worker** | a thread that takes jobs and runs them |
| **future** | a handle to a result that does not exist yet |
| **completion order** | the order calls finish in, fastest first |
| **race condition** | a result that depends on the exact timing of threads, such as a lost `+= 1` |
| **read-modify-write** | read a value, change it, write it back: several steps that a thread can be paused between |
| **lock** | only one thread can hold it at a time; others wait until it is released |
| **deadlock** | two threads each holding a lock the other waits for, so both wait forever |
| **queue** (FIFO) | a first-in, first-out line of items |
| **thread-safe** | safe for many threads at once, without corrupting data |
| **producer** / **consumer** | puts jobs into a queue / takes them out |
| **sentinel** | a special value, often `None`, meaning "stop" |

### Python names and functions

| Name | What it does |
|---|---|
| `from concurrent.futures import ThreadPoolExecutor, as_completed` | the thread-pool tools |
| `ThreadPoolExecutor(max_workers=8)` | a pool of at most 8 threads; leaving its `with` waits for all work |
| `pool.map(func, items)` | runs the calls concurrently, results in input order |
| `pool.submit(func, *args)` | schedules one call and returns a `Future` at once |
| `as_completed(futures)` | hands out futures as they finish |
| `future.result(timeout=5)` | waits for the result (at most 5 s); re-raises the worker's exception |
| `future.done()`, `future.cancel()` | checks without waiting; cancels a call not yet started |
| `threading.Thread(target=f)`, `t.start()`, `t.join()` | create a thread running `f`; start it; wait for it to finish |
| `threading.Lock()`, `with lock:` | a lock; holds it for the block, always releasing it |
| `queue.Queue()`, `q.put(x)`, `q.get()` | a thread-safe queue; add; take (waiting while empty) |
| `time.sleep(s)`, `time.perf_counter()` | wait; measure intervals |
| `while (job := q.get()) is not None:` | take jobs until the sentinel arrives |

### Errors

| Error | Means |
|---|---|
| `OSError` | the family of input/output errors, such as a failed download |
| `RuntimeError` | a general error; here, every function failed |

---

Downloading 50 web pages one after another means 50 waits in a row, and
the program spends almost all of that time doing nothing, waiting for
replies. If the downloads could overlap, the whole job would take about as
long as the slowest single download. **Threads** let one program do several
things at once: each thread is a separate line of execution, with its own
place in the code, sharing the program's memory with the others.

Sharing memory is what makes threads powerful and also what makes them
dangerous: two threads changing the same data at the same moment can corrupt
it. This lesson covers the safe, high-level way to use threads, and the two
tools, locks and queues, that keep shared data correct.

## Concurrency, parallelism and the GIL

Two words first. **Concurrency** means several tasks are in progress at
once, taking turns. **Parallelism** means several tasks are literally running
at the same instant, on different CPU cores.

CPython, the standard Python, has a **Global Interpreter Lock** (the GIL):
only one thread executes Python bytecode at a time. So Python threads give
you concurrency but not parallelism for Python code, and they do **not** make
CPU-heavy Python code faster; a calculation split over four threads still
runs on one core at a time.

They are excellent for **I/O-bound** work, though: work that mostly waits on
something outside the program (input/output). A thread waiting on the
network, a disk or `time.sleep` releases the GIL while it waits, and lets
the others run. Waiting is exactly what can overlap.

- Many slow network calls or file operations: threads (or asyncio, the next
  lesson).
- Heavy computation in Python: processes, which each have their own GIL
  (see the Pro section).

(Python 3.13 ships an experimental free-threaded build without the GIL; the
patterns below stay correct either way.)

## ThreadPoolExecutor

You almost never need to create and manage `threading.Thread` objects
yourself. A **thread pool** keeps a fixed number of worker threads and hands
them calls to run; you give it the work and collect the results:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=8) as pool:
    pages = list(pool.map(download, urls))      # results in input order
```

(A sketch: `download` and `urls` stand for your own function and list.)

`pool.map(func, items)` works like the built-in `map`: it calls `func` on
every item, but spreads the calls over the pool's threads so they overlap,
and gives the results back **in the order of the input**, whichever call
finished first. `max_workers` caps how many run at the same moment. Leaving
the `with` block waits for all work to finish and shuts the threads down.

You can measure the overlap. Five calls that each sleep 0.2 seconds take
about 1 second one after another, but about 0.2 seconds on five threads:

```pycon
>>> import time
>>> from concurrent.futures import ThreadPoolExecutor
>>> def slow_double(x):
...     time.sleep(0.2)                 # stands in for a network call
...     return x * 2
...
>>> start = time.perf_counter()
>>> with ThreadPoolExecutor(max_workers=5) as pool:
...     results = list(pool.map(slow_double, [1, 2, 3, 4, 5]))
...
>>> results
[2, 4, 6, 8, 10]
>>> time.perf_counter() - start < 0.6   # far less than 5 x 0.2s
True
```

## Futures

`pool.submit(func, *args)` schedules one call and returns at once with a
`Future`: a handle to a result that does not exist yet. You can keep working
and collect the result later with `future.result()`, which waits for the call
to finish if it has not already:

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

Piece by piece:

- The dict maps each future back to the url it is downloading, so you know
  which result is which.
- `as_completed(futures)` hands out the futures **in the order they finish**,
  fastest first, rather than the order they were submitted. That lets you
  handle each result as soon as it is ready.
- If the call raised an exception in its thread, `fut.result()` raises that
  same exception in yours. An error in a worker is never lost silently; it
  waits in the future until someone asks for the result.

```pycon
>>> from concurrent.futures import as_completed
>>> def nap(seconds):
...     time.sleep(seconds)
...     return seconds
...
>>> with ThreadPoolExecutor() as pool:
...     futures = [pool.submit(nap, s) for s in (0.3, 0.1, 0.2)]
...     print([f.result() for f in as_completed(futures)])
...
[0.1, 0.2, 0.3]
```

Submitted in the order 0.3, 0.1, 0.2; completed, and printed, shortest first.

`future.result(timeout=5)` waits at most 5 seconds, `future.done()` checks
without waiting, and `future.cancel()` cancels a call that has not started
yet; those round out the API.

## Race conditions

`count += 1` looks like one step, but it is several: read `count`, add one,
write it back. A thread can be paused between any two of them. With two
threads and `count` at 5:

```text
thread A: reads 5
thread B: reads 5          (A was paused before writing)
thread A: writes 6
thread B: writes 6         one increment has been lost
```

Both threads added one, but `count` only went up by one. This is a **race
condition**: the result depends on the exact timing of the threads, so it may
work a thousand times and fail on the next run, which makes it very hard to
debug.

The fix is a **lock** around the whole read-modify-write. Only one thread can
hold a lock at a time; any other thread that tries to take it waits until it
is released. `with lock:` takes the lock on entry and always releases it on
exit, even if the block raises:

```python
import threading

lock = threading.Lock()
with lock:
    count += 1
```

With the lock, eight threads each adding 10,000 always reach exactly 80,000:

```pycon
>>> import threading
>>> class Tally:
...     def __init__(self):
...         self.value = 0
...         self._lock = threading.Lock()
...     def add(self):
...         with self._lock:            # read, add and write as one step
...             self.value += 1
...
>>> t = Tally()
>>> def hammer():
...     for _ in range(10_000):
...         t.add()
...
>>> threads = [threading.Thread(target=hammer) for _ in range(8)]
>>> for th in threads: th.start()
>>> for th in threads: th.join()
>>> t.value
80000
```

`Thread(target=hammer)` creates a thread that will run `hammer`; `start()`
sets it running, and `join()` waits until it has finished.

Some rules for locks:

- Hold locks briefly, only around the shared data, so other threads are not
  kept waiting.
- Never do slow I/O while holding one if you can avoid it.
- When code needs several locks, always acquire them in the same order
  everywhere. Otherwise thread A can hold lock 1 and wait for lock 2 while
  thread B holds lock 2 and waits for lock 1, and both wait forever. That is
  a **deadlock**.

## Queues

`queue.Queue` is a first-in, first-out line of items that is **thread-safe**:
many threads can put and get at once without corrupting it, because it uses
locks inside. It is the simplest correct way to pass work between threads:
**producers** `put` jobs in, **workers** `get` them out. If the queue is
empty, `get()` waits until an item arrives.

A worker needs to know when to stop, and an empty queue does not mean
"finished" (more work may be on its way). The usual signal is a special
value, a **sentinel**, often `None`: on receiving it, a worker leaves its
loop:

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

(A sketch: `handle` and `jobs` stand for your own function and list.)

Each worker takes exactly one sentinel and stops, so four workers need four
`None`s; with fewer, some workers would wait forever and `join()` would never
return. The sentinels go in *after* the jobs, so the workers finish the real
work first.

## Your turn

In `concurrent_tools.py`:

- `fetch_all(urls, fetch, max_workers=8)`: call `fetch(url)` for every url
  concurrently and return the results as a list, in input order. The tests
  use a `fetch` that sleeps 0.2 seconds, and run 16 of them with 16 workers
  in under 1.5 seconds, so doing them one after another is too slow.
- `Counter`: a class with a `value` attribute starting at `0`, and a
  thread-safe `increment()` that adds one. A test runs eight threads that
  call it 20,000 times each, and switches between threads very often to
  expose races; the total must be exactly 160,000.
- `first_success(funcs)`: run the zero-argument functions concurrently and
  return the first result that did not raise, in completion order (the
  fastest successful one, not the first in the list). If all of them raise,
  raise `RuntimeError`.
- `worker_pipeline(items, process, n_workers)`: process all items with
  `n_workers` threads fed from a `queue.Queue` and stopped with sentinels;
  return the **sorted** list of results. The work must really be shared
  (a test checks more than one thread ran `process`), and every worker
  thread must have finished when the function returns.
