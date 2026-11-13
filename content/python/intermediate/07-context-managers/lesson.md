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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **context manager** | an object that packages setup and cleanup, used with `with` |
| **setup** / **cleanup** | the first half of a paired job (open, lock) / the second half (close, release) |
| **context manager protocol** | the two special methods `__enter__` and `__exit__` |
| **`__enter__`** | called on entering the `with`; what it returns goes to the name after `as` |
| **`__exit__(exc_type, exc, tb)`** | called on leaving, always; told the exception's type, object and traceback (all `None` if none) |
| **suppress** (swallow) | stop an exception so the program carries on after the `with`; `__exit__` does it by returning a true value |
| **propagate** | let an exception carry on upwards to the caller |
| **`BaseException`** | the parent of every exception, including Ctrl+C's `KeyboardInterrupt` |
| **generator-based context manager** | a generator split at its one `yield`: setup before, cleanup after |
| **current working directory** | the folder relative paths are looked up in |
| **standard output** (stdout) | where `print` writes, normally the terminal |
| **lock** | a guard that lets only one thread at a time into some code |
| **transaction** | changes that are applied all together, or not at all |
| **in place** | changing the caller's own dict rather than a new one |

### Python names and functions

| Name | What it does |
|---|---|
| `with mgr as name:` | calls `__enter__`, runs the block, then always calls `__exit__` |
| `return False` (in `__exit__`) | do not swallow the exception |
| `time.perf_counter()`, `time.sleep(s)` | a clock for intervals; wait `s` seconds |
| `from contextlib import contextmanager` | the decorator that turns a generator into a context manager |
| `try: yield ... finally: ...` | makes the cleanup run even when the block raises |
| `raise` (bare) | re-raises the exception being handled |
| `contextlib.suppress(*exceptions)` | ignores those exception types in its block |
| `contextlib.chdir(path)` | changes directory for the block, then back |
| `contextlib.redirect_stdout(f)` | sends `print` output in the block to `f` |
| `contextlib.ExitStack()`, `stack.enter_context(m)` | manages any number of context managers, closing them all at the end |
| `os.chdir(path)`, `os.getcwd()` | change the current directory; tell you the current one |
| `os.remove(path)` | deletes a file |
| `tempfile.TemporaryDirectory()` | a folder deleted when the `with` ends |
| `except (KeyError, ZeroDivisionError):` | `except` accepts a tuple of exception types |
| `d.copy()`, `d.clear()`, `d.update(other)` | a shallow copy; empty the dict; copy pairs in |

### Errors

| Error | Means |
|---|---|
| `ZeroDivisionError` | the example's error raised inside a `with` block |
| `FileNotFoundError` | removing a file that is not there (suppressed in the example) |
| `KeyboardInterrupt` | Ctrl+C; a `BaseException`, so `with` still cleans up |

---

Many jobs come in pairs: open a file and close it, take a lock and release
it, change a setting and change it back. The second half is easy to forget,
and easier still to skip by accident, when an exception jumps out of the
middle before the clean-up line is reached. A **context manager** is an
object that packages both halves, and the `with` statement guarantees that
setup is paired with cleanup, even when the block raises:

```python
with open("data.txt") as f:
    data = f.read()
# the file is closed here, exception or not
```

You have used this since the Files lesson. This lesson shows what `with`
actually does, so you can write context managers of your own.

## The protocol

Any object with two special methods, `__enter__` and `__exit__`, works in a
`with`. When Python runs `with something as name:`, the steps are:

1. Work out `something`, which gives the context manager object.
2. Call its `__enter__()`. Whatever that returns is put in `name` (the
   `as name` part is optional).
3. Run the indented block.
4. Call its `__exit__(...)`, whether the block finished normally or raised.

Printing from each method shows the order:

```pycon
>>> class Noisy:
...     def __enter__(self):
...         print("enter")
...         return "the value for as"
...     def __exit__(self, exc_type, exc, tb):
...         print("exit, exception was:", exc_type)
...         return False
...
>>> with Noisy() as v:
...     print("block got:", v)
...
enter
block got: the value for as
exit, exception was: None
```

And when the block raises, `__exit__` still runs before the error carries on
upwards:

```text
>>> with Noisy():
...     1 / 0
...
enter
exit, exception was: <class 'ZeroDivisionError'>
Traceback (most recent call last):
  ...
ZeroDivisionError: division by zero
```

`exit` is printed before the traceback: `__exit__` ran first, was told which
exception happened, returned `False`, and only then did the error continue
on its way.

A useful context manager does real work in those methods. This one measures
how long its block takes:

```pycon
>>> import time
>>> class Timer:
...     def __enter__(self):
...         self.start = time.perf_counter()
...         return self                        # bound to the name after `as`
...     def __exit__(self, exc_type, exc, tb):
...         self.elapsed = time.perf_counter() - self.start
...         return False                       # do not swallow exceptions
...
>>> with Timer() as t:
...     time.sleep(0.1)
...
>>> 0.09 < t.elapsed < 1
True
```

`__enter__` returns `self`, so `t` is the `Timer` object itself, and after the
block `t.elapsed` holds the seconds taken (a little over 0.1 here; the exact
number varies, which is why the example checks a range instead of printing
it).

`__exit__` receives three arguments describing what happened in the block:
the exception's type, the exception object, and its traceback. When the block
finished normally, all three are `None`. Its return value decides what
happens next. If it returns a true value, the exception is **suppressed**:
it stops there, and the program carries on after the `with` as if nothing
had gone wrong. Return `False` (or nothing, which is `None` and also false)
unless suppressing is the point; otherwise errors vanish without a trace.

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

(A sketch, not something to run: `...block...` stands for your code.)
`BaseException` is the parent of every exception, including Ctrl+C's
`KeyboardInterrupt`, so the clean-up runs whatever went wrong. A bare
`raise` inside `except` re-raises the exception being handled.

## @contextmanager

Writing a class with two special methods is a lot of ceremony for a simple
case. The `contextlib` module can turn a generator function into a context
manager instead. The function's code is split at its single `yield`:

- the code **before** `yield` is the setup, run on entering the `with`;
- the value it yields is what `as` receives;
- the code **after** `yield` is the cleanup, run on leaving the `with`.

```pycon
>>> from contextlib import contextmanager
>>> @contextmanager
... def tag(name):
...     print(f"<{name}>")
...     try:
...         yield name.upper()
...     finally:
...         print(f"</{name}>")
...
>>> with tag("p") as t:
...     print("inside, got", t)
...
<p>
inside, got P
</p>
```

The `try` / `finally` matters. If the `with` block raises, the exception is
raised inside the generator **at the `yield`**, as if the `yield` line itself
had failed. Without `finally`, the lines after `yield` would be skipped, and
the cleanup would never run, which is exactly what a context manager exists
to prevent. Writing `try: yield` / `finally: cleanup` makes the cleanup run
either way.

A real one looks the same, with real setup and cleanup in place of the
prints (a fragment: `connect` stands for whatever opens your database):

```python
@contextmanager
def opened_db(path):
    conn = connect(path)
    try:
        yield conn
    finally:
        conn.close()
```

To suppress an exception in a generator-based context manager, catch it
around the `yield` with `try` / `except` instead of letting it pass through.

## Ready-made tools in contextlib

The module ships with several context managers for common needs:

- `suppress(*exceptions)` ignores the listed exception types inside its
  block. It is a short, explicit form of `try` / `except ...: pass`.
- `chdir(path)` changes the current directory for the block and changes it
  back afterwards.
- `redirect_stdout(f)` sends everything `print`ed in the block to `f`
  instead of the terminal.
- `ExitStack()` manages a number of context managers that is only known
  while the program runs, such as one open file per item in a list, and
  closes them all at the end.

```pycon
>>> import os
>>> from contextlib import suppress
>>> with suppress(FileNotFoundError):
...     os.remove("no-such-file.tmp")      # would raise; suppressed instead
...
>>> print("carried on")
carried on
```

`ExitStack` in use (a fragment: `paths` is a list of file names):

```python
from contextlib import ExitStack

with ExitStack() as stack:                 # a dynamic number of managers
    files = [stack.enter_context(open(p)) for p in paths]
    # every file is open here
# and every file is closed here
```

## Common uses

Locks in threaded code (`with lock:`), temporary directories
(`tempfile.TemporaryDirectory()`), database transactions, changing and
restoring global state, timing, and anything else shaped like "do X, and
always undo it". Whenever you write a `try` / `finally` whose only job is to
undo something, consider making it a context manager so that every caller
gets the clean-up for free.

## Your turn

In `contexts.py`:

- `Timer`: a class-based context manager; after the block, `.elapsed` holds
  the seconds taken, as a float. Exceptions from the block must not be
  swallowed, and `.elapsed` must be set even when the block raises.
- `changed_dir(path)`: a `@contextmanager` that switches the current working
  directory to `path` (`os.chdir`) for the block, and **always** switches
  back to the directory it started in, even if the block raises.
  (`os.getcwd()` tells you the current one.)
- `ignore_errors(*exception_types)`: suppresses only the given exception
  types. `with ignore_errors(KeyError, ZeroDivisionError):` hides those two;
  any other exception passes through as normal.
- `Transaction(data)`: `with Transaction(d) as working:` hands out a copy of
  the dict, and the block makes its changes to the copy. `d` must not change
  while the block is running. If the block finishes normally, `d` is updated
  to match the copy exactly, including keys the block deleted; if it raises,
  `d` is left exactly as it was and the exception propagates. Update `d`
  itself, in place, since the caller still holds that same dict.
