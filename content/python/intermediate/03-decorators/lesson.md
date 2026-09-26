---
title: Decorators
summary: Wrap functions to add behaviour, keep their identity with functools.wraps, and write decorators that take arguments.
order: 3
files: [decorators.py]
run: python -i decorators.py
hints:
  - "Every decorator here has the same shape: `def deco(func): @functools.wraps(func) def wrapper(*args, **kwargs): ... return func(*args, **kwargs); return wrapper`."
  - "`count_calls`: store the count on the wrapper itself, `wrapper.calls = 0`, and `wrapper.calls += 1` inside."
  - "`retry(times)` has three levels: `retry(times)` returns a decorator, which returns a wrapper. Loop `for attempt in range(times)`, `try: return func(...)`, and re-raise after the last failure."
  - "`memoize`: a dict keyed by `args`; `if args not in cache: cache[args] = func(*args)`."
---

A **decorator** is a function that takes a function and returns a replacement.
The `@` syntax is shorthand:

```python
@timer
def build_report(): ...

# is exactly
def build_report(): ...
build_report = timer(build_report)
```

## Writing one

```python
import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.perf_counter() - start:.3f}s")
        return result
    return wrapper
```

- `wrapper(*args, **kwargs)` accepts any arguments and passes them straight on,
  so the decorator works on any function.
- Always `return func(...)`'s result, or the decorated function returns `None`.
- `wrapper` is a closure: it remembers `func`.

## functools.wraps

Without it, the decorated function takes the wrapper's identity:

```python
build_report.__name__     # 'wrapper'   without wraps
build_report.__name__     # 'build_report' with wraps
```

`wraps` copies the name, docstring and more, and sets `__wrapped__` to the
original. Debuggers, `help()` and test tools rely on these. Always use it.

## Attaching state

Functions are objects, so a wrapper can carry attributes:

```python
def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper
```

## Decorators with arguments

This is the one that catches people out, so build it up rather than reading it
whole.

Everything above had **two** levels: a decorator that takes a function, and a
wrapper inside it. But `@repeat(3)` is not a decorator - it is a **call**.
Python evaluates `repeat(3)` first, and whatever comes back is then used as the
decorator:

```python
@repeat(3)
def ping(): print("ping")

# is exactly
def ping(): print("ping")
ping = repeat(3)(ping)          # note the two sets of brackets
```

So `repeat(3)` has to *return a decorator*, which means one more level. Three
functions, each with one job:

```python
def repeat(n):                              # 1. takes the ARGUMENTS
    def decorator(func):                    # 2. takes the FUNCTION
        @functools.wraps(func)
        def wrapper(*args, **kwargs):       # 3. takes the CALL's arguments
            for _ in range(n):
                result = func(*args, **kwargs)
            return result
        return wrapper                      # 2 returns 3
    return decorator                        # 1 returns 2
```

Read the returns from the bottom up: `repeat` returns `decorator`, `decorator`
returns `wrapper`, and `wrapper` is what `ping` becomes. Each level closes over
what the level above it was given - `wrapper` can still see `n`, three levels
up, because it is a closure.

The shape is always the same, and it is worth memorising as a shape:
arguments, then function, then call.

## Stacking

```python
@a
@b
def f(): ...          # f = a(b(f)): the decorator nearest the function applies first
```

## In the standard library

`@functools.lru_cache`, `@functools.cache`, `@property`, `@staticmethod`,
`@classmethod`, `@dataclasses.dataclass`, `@contextlib.contextmanager`. You will
write several of these patterns yourself in later lessons.

## Your turn

In `decorators.py`, using `functools.wraps` in each:

- `count_calls`: the wrapper has a `.calls` attribute counting calls
- `retry(times)`: the hard one - a decorator with arguments, so three levels
  as above. Call the function up to `times` times until it does not raise; if
  every attempt raises, re-raise the last exception
- `memoize`: cache results by positional arguments so the function body runs
  once per distinct argument tuple
- `uppercase_result`: upper-case whatever string the function returns
