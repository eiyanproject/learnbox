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

`asyncio` runs many tasks **concurrently in one thread**. Where threads are
switched preemptively by the OS, async code switches only at `await`, which
makes shared state far easier to reason about. It shines for large numbers of
network connections.

## Coroutines and the event loop

```python
import asyncio

async def greet(name, delay):
    await asyncio.sleep(delay)      # yields control while waiting
    return f"hi {name}"

asyncio.run(greet("ana", 1))        # start an event loop, run until done
```

- `async def` defines a **coroutine function**. Calling it returns a coroutine
  object and runs **nothing** yet.
- `await x` runs `x` and suspends this coroutine until it finishes, letting the
  event loop run other tasks meanwhile.
- `asyncio.run` is the entry point from ordinary code.

Never call blocking functions (`time.sleep`, `requests.get`, heavy loops) inside
a coroutine: they freeze **every** task. Use the async version, or push blocking
work to a thread with `await asyncio.to_thread(func, *args)`.

## Running things concurrently

`await a(); await b()` is still sequential. To overlap:

```python
results = await asyncio.gather(fetch(1), fetch(2), fetch(3))   # in order

task = asyncio.create_task(fetch(4))    # starts running in the background
...
result = await task
```

`TaskGroup` (3.11+) is the structured version: if one task fails, the others are
cancelled, and errors are raised together:

```python
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(fetch(1))
    t2 = tg.create_task(fetch(2))
print(t1.result(), t2.result())
```

## Timeouts and cancellation

```python
try:
    data = await asyncio.wait_for(fetch(url), timeout=2)
except TimeoutError:
    data = None

async with asyncio.timeout(2):          # 3.11+
    data = await fetch(url)
```

Timeouts work by **cancelling** the task: a `CancelledError` is raised at its
current `await`. Clean up in `finally`, and do not swallow `CancelledError`.

## Limiting concurrency

Starting 10,000 requests at once will get you rate-limited or run out of file
descriptors. A semaphore caps how many run at a time:

```python
sem = asyncio.Semaphore(10)

async def polite_fetch(url):
    async with sem:
        return await fetch(url)
```

## Async iteration

```python
async def ticks(n):
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i                     # an async generator

async for t in ticks(3): ...
values = [t async for t in ticks(3)]
```

`async with` and `async for` are the async versions of context managers and
iterators (`__aenter__`/`__aexit__`, `__aiter__`/`__anext__`).

## Your turn

In `async_tools.py` (tests call these with `asyncio.run`):

- `fetch_all(urls, fetch)`: run the async `fetch(url)` for all urls
  concurrently; results in input order
- `fetch_with_timeout(coro, timeout, default=None)`: await `coro`, or return
  `default` if it takes longer than `timeout` seconds
- `limited_gather(urls, fetch, limit)`: like `fetch_all`, but never more than
  `limit` fetches running at once
- `ticker(n, delay)`: an async generator yielding `0..n-1`, sleeping `delay` before each
- `collect(agen)`: a list of everything an async iterator produces
