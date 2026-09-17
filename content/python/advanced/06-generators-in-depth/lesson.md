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

```python
def echo():
    received = None
    while True:
        received = yield f"got {received}"

g = echo()
next(g)            # 'got None'   run to the first yield ("priming")
g.send("hi")       # 'got hi'
g.send(42)         # 'got 42'
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

```python
def collect():
    items = []
    while (x := (yield)) is not None:
        items.append(x)
    return items

g = collect(); next(g)
g.send(1); g.send(2)
try:
    g.send(None)
except StopIteration as stop:
    stop.value        # [1, 2]
```

## yield from, fully

`yield from sub` does more than loop over `sub`: it passes `send`, `throw` and
`close` straight through to the sub-generator, and **evaluates to its return
value**. That makes it possible to split a coroutine into smaller ones:

```python
def outer():
    while True:
        batch = yield from collect()     # delegate until collect returns
        print("batch done:", batch)
```

This delegation is exactly what `async`/`await` grew out of; the Asyncio lesson
builds on it.

## When to use it

Stateful stream processing (running statistics, parsers fed one token at a
time, protocol state machines) without writing a class. For most other
concurrency needs, `asyncio` is the modern tool.

## Your turn

In `coroutines.py`:

- `primed(genfunc)`: decorator that advances a new generator to its first `yield`
- `running_average()`: a primed coroutine; each `send(x)` returns the average
  of everything sent so far
- `accumulate_until_none()`: a coroutine that sums the numbers sent to it and,
  when sent `None`, **returns** the total
- `batch_totals(results)`: a primed coroutine that repeatedly delegates to
  `accumulate_until_none()` with `yield from`, appending each batch's total to
  the `results` list it was given
