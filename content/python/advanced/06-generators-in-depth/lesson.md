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

In the Intermediate section, generators only produced values: each `next()`
pulled one out. But the conversation can go the other way. A generator can
also **receive** values while it is paused, which turns it into a small
**coroutine**: a function that can be paused and resumed many times, keeping
private state in its local variables between visits. That makes it a neat
way to process a stream of values one at a time, such as keeping a running
average of numbers as they arrive, without writing a class.

This lesson is also the background for the Asyncio lesson: `async` and
`await` grew directly out of these mechanisms.

## send

So far `yield` has been a statement that hands a value out. It is also an
**expression**: it has a value of its own, which is whatever the caller
sends in when it resumes the generator. `gen.send(value)` resumes the
generator and makes the paused `yield` evaluate to `value`:

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

The line `received = yield f"got {received}"` does two things at two
different moments, which is the confusing part:

1. When execution reaches it, the generator hands out `f"got {received}"`
   and pauses.
2. Later, when someone calls `g.send(x)`, the generator wakes up *on the
   same line*, the `yield` expression evaluates to `x`, and that is assigned
   to `received`. The loop then comes back round, reaches the `yield` again,
   hands out the new text, and pauses once more.

So each `send` both delivers a value in and gets the next value out.

A new generator has not reached any `yield` yet, so there is nothing waiting
to receive a value. The first call must be `next(g)` (or `g.send(None)`),
which runs the body up to the first `yield`. This is called **priming**.
Sending anything other than `None` to an unprimed generator is a
`TypeError`:

```pycon
>>> fresh = echo()
>>> fresh.send("too early")
Traceback (most recent call last):
  ...
TypeError: can't send non-None value to a just-started generator
```

A small decorator removes that step, creating the generator and priming it
in one go (this is the first part of the exercise):

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

Two more methods let the caller reach into a paused generator:

- `gen.throw(exc)` raises the exception `exc` **at the paused `yield`**, as
  if that line had raised it. The generator can catch it with `try` /
  `except` and carry on, or let it propagate back out to the caller.
- `gen.close()` raises the special exception `GeneratorExit` at the paused
  `yield`. The generator is expected to finish, so any `finally` blocks run:
  generators clean up after themselves.

```pycon
>>> def worker():
...     try:
...         while True:
...             job = yield
...             print("processing", job)
...     except ValueError as e:
...         print("worker got an error:", e)
...         yield "recovered"
...     finally:
...         print("cleaning up")
...
>>> w = worker(); next(w)
>>> w.send("job 1")
processing job 1
>>> w.throw(ValueError("bad input"))
worker got an error: bad input
'recovered'
>>> w.close()
cleaning up
```

`throw` raised the `ValueError` at the paused `job = yield`; the outer
`except` caught it, printed, and yielded `"recovered"`, which became the
return value of `throw`. `close()` then raised `GeneratorExit` at that last
`yield`, nothing caught it, and on the way out the `finally` block ran.
Python also calls `close()` on a generator when it is garbage collected, so
`finally` clean-up happens even if nobody remembers to call it.

## Returning a value

A generator can `return value`, like a function. Since the caller is
receiving values through `next` or `send`, the return value cannot be
handed out the normal way. It travels inside the `StopIteration` that ends
the generator, as its `.value` attribute:

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

Two new pieces of syntax here:

- `(yield)` on its own yields `None` and evaluates to what is sent in.
- `x := ...` is the **walrus operator**: it assigns a value to `x` and also
  gives that value to the surrounding expression. So
  `while (x := (yield)) is not None:` means "receive a value into `x`, and
  keep looping as long as it is not `None`".

Sending 1 and 2 adds them to `items`. Sending `None` ends the loop, the
function returns `items`, and the `send` raises `StopIteration` carrying
`[1, 2]`.

Catching `StopIteration` by hand like this is clumsy. You rarely need to,
because of the next section.

## yield from, fully

In the Intermediate section, `yield from sub` looked like a shortcut for
`for x in sub: yield x`. It does more than loop over `sub`:

- it passes `send`, `throw` and `close` from the caller straight through to
  the sub-generator, so the caller talks to the sub-generator directly
  without knowing it exists;
- and the whole `yield from` expression **evaluates to the sub-generator's
  return value**, catching the `StopIteration` for you.

That makes it possible to split a coroutine into smaller ones, the way a
function calls helper functions:

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

Following it through: priming `o` runs `outer` up to `yield from collect()`,
which starts `collect` and runs it to its first `yield`. Sending `"a"` and
`"b"` goes straight through `outer` into `collect`. Sending `None` makes
`collect` return `["a", "b"]`, so `yield from` evaluates to that list and
`outer` prints it. The loop then starts a fresh `collect()` for the next
batch.

This delegation is exactly what `async`/`await` grew out of; the Asyncio
lesson builds on it. `await something` is, underneath, very close to
`yield from something`.

## When to use it

Coroutines built this way suit **stateful stream processing**: running
statistics, parsers fed one token at a time, protocol state machines that
react to each incoming message. The state lives in ordinary local variables,
with no class needed. For most other concurrency needs, such as waiting on
many network connections at once, `asyncio` (two lessons from now) is the
modern tool.

## Your turn

In `coroutines.py`:

- `primed(genfunc)`: a decorator. Calling the decorated function creates the
  generator and advances it to its first `yield`, so the caller can `send`
  to it straight away. Use `functools.wraps`, so the decorated function keeps
  its name.
- `running_average()`: a primed coroutine. Each `send(x)` returns the average
  of everything sent so far: after `avg = running_average()`, `avg.send(10)`
  is `10.0` and `avg.send(20)` is `15.0`. Two separate `running_average()`s
  keep separate totals.
- `accumulate_until_none()`: a coroutine (not primed; the caller calls
  `next()` first) that adds up the numbers sent to it. When it is sent
  `None` it finishes, and **returns** the total (with `return`, which is what
  `yield from` hands back to whoever delegated to it).
- `batch_totals(results)`: a primed coroutine that never finishes by itself.
  In a loop it delegates to a fresh `accumulate_until_none()` with
  `yield from` (a test checks that its source uses `yield from`) and appends
  the total that comes back to the `results` list it was given. So the
  numbers sent to it are split into batches by the `None`s: sending `1`,
  `2`, `None`, `10`, `None` leaves `results` as `[3, 10]`. A `None` with no
  numbers before it is an empty batch, with total `0`.
