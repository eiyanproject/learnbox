---
title: Context managers
summary: How with works, writing your own with a class or @contextmanager, and cleanup you can rely on.
order: 7
files: [contexts.py]
run: python -i contexts.py
hints:
  - "`Timer`: `__enter__` records `time.perf_counter()` and returns `self`; `__exit__(self, exc_type, exc, tb)` sets `self.elapsed` and returns `False` so exceptions still propagate."
  - "`changed_dir` with `@contextmanager`: save `os.getcwd()`, `os.chdir(path)`, then `try: yield` / `finally: os.chdir(old)`."
  - "`ignore_errors(*types)`: `try: yield` / `except types: pass`. `except` accepts a tuple of exception classes."
  - "`Transaction.__exit__`: if `exc_type is None`, copy the working dict into the real one; otherwise leave it untouched. Return `False` either way."
---

`with` guarantees that setup is paired with cleanup, even when the block
raises:

```python
with open("data.txt") as f:
    data = f.read()
# the file is closed here, exception or not
```

## The protocol

Any object with `__enter__` and `__exit__` works in a `with`:

```python
class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self                        # bound to the name after `as`

    def __exit__(self, exc_type, exc, tb):
        self.elapsed = time.perf_counter() - self.start
        return False                       # do not swallow exceptions

with Timer() as t:
    work()
print(t.elapsed)
```

`__exit__` receives the exception type, value and traceback, or three `None`s
when the block finished normally. If it returns a true value, the exception is
**suppressed**. Return `False` (or nothing) unless suppressing is the point.

Roughly, `with` does this:

```python
mgr = Timer()
value = mgr.__enter__()
try:
    ...block...
except BaseException as e:
    if not mgr.__exit__(type(e), e, e.__traceback__):
        raise
else:
    mgr.__exit__(None, None, None)
```

## @contextmanager

Writing a class for simple cases is a lot of ceremony. `contextlib` turns a
generator into a context manager: code before `yield` is setup, the yielded
value is what `as` receives, code after is cleanup:

```python
from contextlib import contextmanager

@contextmanager
def opened_db(path):
    conn = connect(path)
    try:
        yield conn
    finally:
        conn.close()
```

The `try` / `finally` matters: if the `with` block raises, the exception is
raised **at the `yield`**, and without `finally` the cleanup would be skipped.

## Ready-made tools in contextlib

```python
from contextlib import suppress, redirect_stdout, ExitStack, chdir

with suppress(FileNotFoundError):
    os.remove("maybe.tmp")

with ExitStack() as stack:                 # a dynamic number of managers
    files = [stack.enter_context(open(p)) for p in paths]
```

## Common uses

Locks (`with lock:`), temporary directories (`tempfile.TemporaryDirectory()`),
database transactions, changing and restoring global state, timing,
and anything else shaped like "do X, and always undo it".

## Your turn

In `contexts.py`:

- `Timer`: a class-based context manager; after the block, `.elapsed` holds
  the seconds taken. Exceptions from the block must not be swallowed.
- `changed_dir(path)`: `@contextmanager` that switches the working directory
  and **always** switches back
- `ignore_errors(*exception_types)`: suppresses only the given exception types
- `Transaction(data)`: `with Transaction(d) as working:` hands out a copy of the
  dict. If the block finishes normally, `d` is updated to match the copy; if it
  raises, `d` is left exactly as it was and the exception propagates.
