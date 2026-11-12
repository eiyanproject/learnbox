---
title: asyncio
summary: Coroutines, the event loop, gather, timeouts, limiting concurrency with semaphores, and async iteration.
order: 8
files: [async_tools.py]
run: python -i async_tools.py
hints:
  - "`fetch_all(urls, fetch)`: `return await asyncio.gather(*(fetch(u) for u in urls))`. `gather` keeps input order."
  - "`fetch_with_timeout`: `try: return await asyncio.wait_for(coro, timeout)` / `except TimeoutError: return default`."
  - "`limited_gather`: create `sem = asyncio.Semaphore(limit)` and wrap each call: `async def one(u): async with sem: return await fetch(u)`, then gather those."
  - "`ticker(n, delay)` is an async generator: `for i in range(n): await asyncio.sleep(delay); yield i`. `collect` uses `[x async for x in agen]`."
---

The last lesson overlapped waiting with threads. `asyncio` overlaps it
another way: it runs many tasks **concurrently in one thread**. Each task is
a coroutine (the idea from Generators in depth: a function that can pause
and resume), and a scheduler called the **event loop** runs whichever task
is ready while the others wait.

The key difference from threads is *when* switching happens. The operating
system can switch threads at any moment, even halfway through `count += 1`,
which is why threads need locks. Async code switches only at an `await`, a
point you wrote yourself, so between two `await`s your code runs without
interruption, and shared state is far easier to reason about. It shines for
large numbers of network connections: one thread can juggle thousands of
them, where thousands of threads would be expensive.

## Coroutines and the event loop

```pycon
>>> import asyncio
>>> async def greet(name, delay):
...     await asyncio.sleep(delay)      # yields control while waiting
...     return f"hi {name}"
...
>>> greet("ana", 1)                     # calling it only makes a coroutine...
<coroutine object greet at 0x...>
>>> asyncio.run(greet("ana", 1))        # ...run starts an event loop and runs it
'hi ana'
```

- `async def` defines a **coroutine function**. Calling it returns a coroutine
  object and runs **nothing** yet, the same as calling a generator function.
- `await x` runs `x` and suspends this coroutine until it finishes, letting
  the event loop run other tasks meanwhile. `await` can only be used inside
  an `async def`.
- `asyncio.run(coro)` is the entry point from ordinary code: it starts an
  event loop, runs the coroutine to the end, and returns its result.

(A coroutine object that is never awaited does nothing at all, and Python
warns "coroutine ... was never awaited" when it is thrown away. The bare
`greet("ana", 1)` above triggers that warning; it was only there to show
what calling it returns.)

`asyncio.sleep` is the async version of `time.sleep`. While one coroutine is
sleeping, the loop can run others. That is the whole trick: every `await` on
something slow is a chance for other work to happen.

Never call blocking functions (`time.sleep`, `requests.get`, heavy loops)
inside a coroutine. They do not `await`, so they never give control back, and
they freeze **every** task on the loop until they finish. Use the async
version, or push blocking work to a thread with
`await asyncio.to_thread(func, *args)`.

## Running things concurrently

`await a(); await b()` is still sequential: the first `await` waits for `a`
to finish before `b` even starts. To overlap them, hand several coroutines to
the loop at once. `asyncio.gather` runs them concurrently and returns their
results as a list, in the order you passed them:

```pycon
>>> import time
>>> async def main():
...     start = time.perf_counter()
...     results = await asyncio.gather(greet("a", 0.2), greet("b", 0.2), greet("c", 0.2))
...     return results, time.perf_counter() - start < 0.5
...
>>> asyncio.run(main())                 # three 0.2s waits overlap: about 0.2s
(['hi a', 'hi b', 'hi c'], True)
```

`asyncio.create_task(coro)` starts a coroutine running in the background
right away and gives you a **task** to `await` later, so you can do other
work in the meantime:

```python
task = asyncio.create_task(fetch(4))    # starts running in the background
...                                     # other work here
result = await task
```

`TaskGroup` (3.11+) is the structured version: every task created in the
group is awaited when the `async with` block ends. If one task fails, the
others are cancelled, and the errors are raised together:

```python
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(fetch(1))
    t2 = tg.create_task(fetch(2))
print(t1.result(), t2.result())
```

(Sketches: `fetch` stands for any coroutine function of yours.)

## Timeouts and cancellation

A network call can hang. `asyncio.wait_for(coro, timeout)` waits at most
`timeout` seconds and raises `TimeoutError` if the coroutine has not finished
by then; `asyncio.timeout(seconds)` does the same for a whole block:

```python
try:
    data = await asyncio.wait_for(fetch(url), timeout=2)
except TimeoutError:
    data = None

async with asyncio.timeout(2):          # 3.11+
    data = await fetch(url)
```

```pycon
>>> async def slow():
...     await asyncio.sleep(10)
...     return "done"
...
>>> async def main():
...     try:
...         return await asyncio.wait_for(slow(), timeout=0.1)
...     except TimeoutError:
...         return "gave up"
...
>>> asyncio.run(main())                  # returns after 0.1s, not 10s
'gave up'
```

`except TimeoutError` above also needs **3.11+**, where `asyncio.TimeoutError`
became an alias of the built-in. Before that it aliased
`concurrent.futures.TimeoutError`, and a bare `except TimeoutError:` would not
catch it - so on 3.10 and earlier you must write `except asyncio.TimeoutError:`.

Timeouts work by **cancelling** the task: a `CancelledError` is raised inside
it, at whichever `await` it is paused on, so it stops there. Clean up in
`finally`, and do not swallow `CancelledError` (do not catch it without
re-raising), or the task cannot be stopped and the timeout will not work.

## Limiting concurrency

Starting 10,000 requests at once will get you rate-limited by the server, or
run out of **file descriptors** (the operating system's limited supply of
open connections and files). A **semaphore** caps how many run at a time. It
is like a lock that allows up to N holders instead of one: `async with sem:`
waits until one of the N places is free, takes it, and gives it back when the
block ends:

```python
sem = asyncio.Semaphore(10)

async def polite_fetch(url):
    async with sem:
        return await fetch(url)
```

Gathering 10,000 `polite_fetch` calls then still starts them all, but at most
10 are inside the `async with` block, making a request, at any moment; the
rest wait their turn.

## Async iteration

An `async def` that contains `yield` is an **async generator**. It is like an
ordinary generator, except that it can `await` between values, so it can
produce values that take time to arrive, such as messages from a network
connection. You loop over one with `async for` (inside an `async def`):

```pycon
>>> async def ticks(n):
...     for i in range(n):
...         await asyncio.sleep(0.01)
...         yield i                     # an async generator
...
>>> async def main():
...     seen = []
...     async for t in ticks(3):
...         seen.append(t)
...     return seen, [t async for t in ticks(2)]
...
>>> asyncio.run(main())
([0, 1, 2], [0, 1])
```

`[t async for t in ticks(2)]` is an **async comprehension**, the same idea as
a list comprehension.

`async with` and `async for` are the async versions of context managers and
iterators. They use their own special methods, `__aenter__` / `__aexit__`
and `__aiter__` / `__anext__`, which are coroutines, so setup, cleanup and
fetching the next item can all `await`. An async iterator signals the end by
raising `StopAsyncIteration`, the async counterpart of `StopIteration`.

## Your turn

In `async_tools.py` (the tests call these with `asyncio.run`, so each one is
an `async def` except `ticker`, which is an async generator):

- `fetch_all(urls, fetch)`: run the async `fetch(url)` for all urls
  concurrently; return the results in input order. The tests run 20 fetches
  of 0.2 seconds each and expect them to finish in under 1 second.
- `fetch_with_timeout(coro, timeout, default=None)`: await `coro`, or return
  `default` if it takes longer than `timeout` seconds. It must give up on
  time, not wait for the slow coroutine to finish.
- `limited_gather(urls, fetch, limit)`: like `fetch_all`, but never more than
  `limit` fetches running at once. A test tracks how many run at the same
  time and expects the peak to be exactly `limit`, so they must still overlap
  up to that number.
- `ticker(n, delay)`: an async generator yielding `0..n-1`, sleeping `delay`
  seconds before each.
- `collect(agen)`: a list of everything an async iterator produces, in
  order. It must work on any async iterable, not only async generators.
