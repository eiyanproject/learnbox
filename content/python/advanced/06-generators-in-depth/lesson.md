---
title: Generators in depth
summary: send, throw and close; return values through yield from; and generator-based pipelines with state.
order: 6
files: [coroutines.py]
run: python -i coroutines.py
hints:
  - "`running_average()`: `total = count = 0; average = None`, then `while True: value = yield average; total += value; count += 1; average = total / count`. Callers prime it with `next()` first."
  - "`primed(genfunc)` is a decorator whose wrapper creates the generator, calls `next(gen)` once, and returns it."
  - "`accumulate_until_none()`: loop `value = yield`; `if value is None: return total`. The return value arrives as `StopIteration.value`, and `yield from` hands it back automatically."
  - "`batch_totals(results)` is `@primed` and its whole body is `while True: total = yield from accumulate_until_none(); results.append(total)`."
---

Generators are not only for producing values. A generator can also **receive**
values, which turns it into a small coroutine with private state.

## send

`yield` is an expression. `gen.send(value)` resumes the generator and makes the
paused `yield` evaluate to `value`:

```pycon
>>> def echo():
...     received = None
...     while True:
...         received = yield f"got {received}"
...
>>> g = echo()
>>> next(g)            # run to the first yield ("priming")
'got None'
>>> g.send("hi")
'got hi'
>>> g.send(42)
'got 42'
```

A new generator has not reached any `yield` yet, so the first call must be
`next(g)` (or `g.send(None)`). A small decorator removes that step:

```python
def primed(genfunc):
    @functools.wraps(genfunc)
    def start(*args, **kwargs):
        gen = genfunc(*args, **kwargs)
        next(gen)
        return gen
    return start
```

## throw and close

`gen.throw(exc)` raises an exception **at the paused yield**, so the generator
can handle it. `gen.close()` raises `GeneratorExit` there, which runs any
`finally` blocks: generators clean up after themselves.

```python
def worker():
    try:
        while True:
            job = yield
            process(job)
    finally:
        print("cleaning up")
```

## Returning a value

A generator can `return value`. The value travels inside `StopIteration`:

```pycon
>>> def collect():
...     items = []
...     while (x := (yield)) is not None:
...         items.append(x)
...     return items
...
>>> g = collect(); next(g)
>>> g.send(1); g.send(2)
>>> try:
...     g.send(None)
... except StopIteration as stop:
...     print(stop.value)
...
[1, 2]
```

## yield from, fully

`yield from sub` does more than loop over `sub`: it passes `send`, `throw` and
`close` straight through to the sub-generator, and **evaluates to its return
value**. That makes it possible to split a coroutine into smaller ones:

```pycon
>>> def outer():
...     while True:
...         batch = yield from collect()     # delegate until collect returns
...         print("batch done:", batch)
...
>>> o = outer(); next(o)
>>> o.send("a"); o.send("b")       # passed straight through to collect
>>> o.send(None)                   # collect returns, and outer prints it
batch done: ['a', 'b']
```

This delegation is exactly what `async`/`await` grew out of; the Asyncio lesson
builds on it.

## When to use it

Stateful stream processing (running statistics, parsers fed one token at a
time, protocol state machines) without writing a class. For most other
concurrency needs, `asyncio` is the modern tool.

## Your turn

In `coroutines.py`:

- `primed(genfunc)`: a decorator. Calling the decorated function creates the
  generator and advances it to its first `yield`, so the caller can `send`
  to it straight away.
- `running_average()`: a primed coroutine. Each `send(x)` returns the average
  of everything sent so far: after `avg = running_average()`, `avg.send(10)`
  is `10.0` and `avg.send(20)` is `15.0`.
- `accumulate_until_none()`: a coroutine that adds up the numbers sent to it.
  When it is sent `None` it finishes, and **returns** the total (with
  `return`, which is what `yield from` hands back to whoever delegated to
  it).
- `batch_totals(results)`: a primed coroutine that never finishes by itself.
  In a loop it delegates to a fresh `accumulate_until_none()` with
  `yield from` and appends the total that comes back to the `results` list
  it was given. So the numbers sent to it are split into batches by the
  `None`s: sending `1`, `2`, `None`, `10`, `None` leaves `results` as
  `[3, 10]`.
