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

Say you want to time ten different functions, or log every call to them,
or retry them when they fail. You could paste the same few lines into each
one, but then the extra code is mixed in with what each function is really
for, and repeated ten times. A **decorator** lets you write that extra
behaviour once and apply it to any function with a single line.

A decorator is a function that takes a function and returns a replacement
for it, usually a new function that does something extra and calls the
original along the way. This builds directly on the last two lessons:
functions are values that can be passed and returned, and an inner function
can remember the function it was given.

The `@` syntax, placed on the line above a `def`, is shorthand:

```python
@timer
def build_report(): ...

# is exactly
def build_report(): ...
build_report = timer(build_report)
```

The function is defined as normal, then passed to `timer`, and whatever
`timer` returns is stored under the name `build_report`. From then on, every
call to `build_report()` is a call to that replacement. (`...` as a function
body is a placeholder that does nothing, like `pass`.)

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


@timer
def slow_sum(n):
    return sum(range(n))

print(slow_sum(10_000_000))
```

Running it prints something like this. The time depends on the machine, so
yours will differ:

```text
slow_sum took 0.142s
49999995000000
```

The timing line comes first because `wrapper` prints it as soon as the
original function finishes, before returning the result to the `print` that
called it.

`timer` runs once, when the decorated function is defined. It does not time
anything itself; it builds `wrapper` and returns it. `wrapper` is what runs on
every call: it notes the time, calls the original function, works out how
long that took and prints it, then hands back the original's result.
`time.perf_counter()` is a clock meant for measuring short intervals: one
reading means nothing on its own, but the difference between two is a
precise number of seconds. `func.__name__` is the name the function was
defined with, so the message says which function was timed.

The important details:

- `wrapper(*args, **kwargs)` accepts any arguments and passes them straight on,
  so the decorator works on any function, whatever parameters it has.
- Always `return` the result of calling `func(...)`, or the decorated function
  returns `None` and anyone using its result gets nothing.
- `wrapper` is a closure: it remembers `func`, the original function, even
  though `timer` has long since returned.
- `@functools.wraps(func)` is itself a decorator, applied to `wrapper`. The
  next section shows what it is for.

## functools.wraps

After decorating, the name `build_report` refers to `wrapper`, a different
function. Without `functools.wraps`, everything that describes the function,
its name and its docstring, now describes the wrapper instead:

```python
import functools

def plain(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def wrapped(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@plain
def build_report(): ...

@wrapped
def build_summary(): ...

print(build_report.__name__)     # without wraps
print(build_summary.__name__)    # with wraps
```

```output
wrapper
build_summary
```

`wraps` copies the name, docstring and a few other details from the original
onto the wrapper, and sets `__wrapped__` on the wrapper to point at the
original. Debuggers, `help()`, error messages and test tools rely on these;
without them, every decorated function in a traceback would be called
`wrapper`. It costs one line, so always use it.

## Attaching state

Functions are objects, so you can set attributes on them the same way you would
on any object, and a wrapper can use that to carry state between calls:

```python
def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper
```

`wrapper.calls = 0` runs once, when the decorator is applied. `wrapper.calls
+= 1` runs on every call. Because the decorated name *is* `wrapper`, the
count can be read from outside: after decorating `greet` with this and calling
it twice, `greet.calls` is 2. Using an attribute rather than a local variable
means no `nonlocal` is needed, and the count is visible to the caller.

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
import functools

def repeat(n):                              # 1. takes the ARGUMENTS
    def decorator(func):                    # 2. takes the FUNCTION
        @functools.wraps(func)
        def wrapper(*args, **kwargs):       # 3. takes the CALL's arguments
            for _ in range(n):
                result = func(*args, **kwargs)
            return result
        return wrapper                      # 2 returns 3
    return decorator                        # 1 returns 2

@repeat(3)
def ping():
    print("ping")

ping()
```

```output
ping
ping
ping
```

Read the returns from the bottom up: `repeat` returns `decorator`, `decorator`
returns `wrapper`, and `wrapper` is what `ping` becomes. Each level closes over
what the level above it was given - `wrapper` can still see `n`, three levels
up, because it is a closure.

`for _ in range(n)` uses `_` as the loop variable, the conventional name for
"a value I do not need": the loop only exists to repeat `n` times.

The shape is always the same, and it is worth memorising as a shape:
arguments, then function, then call. When a decorator with arguments goes
wrong, it is almost always because one of the three levels is missing, or a
level returns the wrong one of the other two.

## Stacking

Several decorators can be applied to one function by stacking them, one per
line. They are applied from the bottom up, starting with the one nearest the
`def`:

```python
@a
@b
def f(): ...          # f = a(b(f)): the decorator nearest the function applies first
```

So `b` wraps the original `f`, and `a` wraps the result of that. When the
final function is called, `a`'s wrapper runs first (it is the outermost
layer), and calls into `b`'s wrapper, which calls the real `f`. The order can
matter: timing a function that is cached gives a different answer from
caching a function that is timed.

You can watch the order with two decorators that label what they wrap:

```python
def a(func):
    return lambda: "a(" + func() + ")"

def b(func):
    return lambda: "b(" + func() + ")"

@a
@b
def f():
    return "f"

print(f())
```

```output
a(b(f))
```

## In the standard library

Python ships with many decorators. A few you will meet often:

- `@functools.cache` and `@functools.lru_cache`: remember results, as the
  `memoize` exercise below does (`lru_cache` keeps only a limited number).
- `@property`, `@staticmethod` and `@classmethod`: change how a method in a
  class behaves (Advanced section).
- `@dataclasses.dataclass`: writes `__init__`, `__repr__` and `__eq__` for a
  class, as you saw at the end of the Beginner section. (A decorator can be
  applied to a class as well as to a function.)
- `@contextlib.contextmanager`: turns a generator into something you can use
  with `with` (a later lesson in this section).

You will write several of these patterns yourself in later lessons.

## Your turn

In `decorators.py`, write four decorators, using `functools.wraps` in each:

- `count_calls`: the decorated function gains a `.calls` attribute that
  starts at `0` and goes up by one every time it is called. After two calls
  of a decorated `add`, `add.calls` is `2`.
- `retry(times)`: the hard one - a decorator with arguments, so three levels
  as above, used as `@retry(3)`. Call the function, and if it raises an
  exception, call it again, up to `times` calls in total. Return the first
  result that comes back without an exception. If every call raises, let the
  last exception through to the caller (a bare `raise` inside an `except`
  block re-raises the exception being handled).
- `memoize`: remember the result for each set of positional arguments. The
  second time the function is called with the same arguments, return the
  remembered result without running the function body again. Inside the
  wrapper, `args` is a tuple, and tuples can be dict keys, so a dict from
  `args` to result is all the memory you need.
- `uppercase_result`: call the function, and return whatever string it
  returns in upper case.
