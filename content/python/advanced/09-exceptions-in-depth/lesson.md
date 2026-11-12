---
title: Exceptions in depth
summary: Exception hierarchies, chaining with from, notes, ExceptionGroup and except*, and cleanup that always runs.
order: 9
files: [errors.py]
run: python -i errors.py
hints:
  - "The hierarchy: `class AppError(Exception)`, then `class ConfigError(AppError)` and `class NetworkError(AppError)`. `NetworkError.__init__(self, message, retryable)` calls `super().__init__(message)` and stores `retryable`."
  - "`load_port`: `try: port = int(raw[\"port\"])` / `except (KeyError, ValueError) as e: raise ConfigError(\"invalid port\") from e`."
  - "`validate_all`: collect errors in a list; `if errors: raise ExceptionGroup(\"validation failed\", errors)`."
  - "`count_by_kind`: `try: validate_all(records)` / `except* ValueError as eg: counts[\"value\"] = len(eg.exceptions)` / `except* KeyError as eg: ...`. Each `except*` sees only its matching part of the group."
---

The Beginner section covered raising and catching single errors. Larger
programs need more: errors organised so callers can catch exactly the ones
they care about, low-level errors translated into meaningful ones without
losing the original, extra context attached on the way up, and several
errors reported together when several things fail at once. Python has a tool
for each, and this lesson goes through them in turn.

## Design an exception hierarchy

`except SomeError` also catches every **subclass** of `SomeError`. That makes
a family of exception classes useful. Libraries define one base exception, and
make all their specific errors subclasses of it, so callers can catch
"anything from this library" or something specific:

```python
class PaymentError(Exception):
    """Base for everything this module raises."""

class CardDeclined(PaymentError):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code

class GatewayTimeout(PaymentError):
    pass

try:
    charge(card)
except CardDeclined as e:
    tell_user(e.code)
except PaymentError:
    retry_later()
```

(A sketch: `charge`, `tell_user` and `retry_later` stand for real code.)

Python checks the `except` clauses from the top and runs the first that
matches. A declined card matches `CardDeclined` and the user is told the
reason. A gateway timeout is not a `CardDeclined`, but it is a
`PaymentError`, so the second clause catches it. Order matters: put the
specific classes before the general one, or the general clause would catch
everything first.

A few rules for designing one:

- Subclass `Exception`, not `BaseException`. `BaseException` is also the
  parent of `KeyboardInterrupt` (Ctrl+C) and `SystemExit` (`sys.exit()`),
  which are not errors and should not be caught by `except Exception`.
- Put useful data in attributes, not only in the message. `e.code` can be
  checked by code; text inside a message can only be read by a human.
- Call `super().__init__(message)` from a custom `__init__`, so that
  `str(e)` still gives the message.

```pycon
>>> class PaymentError(Exception):
...     pass
...
>>> class CardDeclined(PaymentError):
...     def __init__(self, message, code):
...         super().__init__(message)
...         self.code = code
...
>>> try:
...     raise CardDeclined("insufficient funds", code=51)
... except PaymentError as e:           # caught through its base class
...     print(type(e).__name__, str(e), e.code)
...
CardDeclined insufficient funds 51
```

## Chaining: raise ... from

A function that reads a config file might hit a `KeyError` or a `ValueError`
deep inside. Its callers should not have to know that; they want a
`ConfigError`. But throwing the original away would also throw away the
clue to what went wrong. `raise ... from` translates a low-level error into
your own without losing the cause:

```python
try:
    port = int(config["port"])
except (KeyError, ValueError) as e:
    raise ConfigError("port missing or not a number") from e
```

An `except` clause can list several types in a tuple, as here, to handle
them the same way.

The traceback then shows both, the original first, joined by the line "The
above exception was the direct cause of the following exception". In code,
the original is on the new exception's `__cause__` attribute:

```pycon
>>> class ConfigError(Exception):
...     pass
...
>>> def load(config):
...     try:
...         return int(config["port"])
...     except (KeyError, ValueError) as e:
...         raise ConfigError("port missing or not a number") from e
...
>>> try:
...     load({"port": "http"})
... except ConfigError as err:
...     print(repr(err.__cause__))
...
ValueError("invalid literal for int() with base 10: 'http'")
```

There are two other cases:

- `raise NewError() from None` hides the cause, for when it would only be
  noise. The traceback then shows only the new error, and
  `__suppress_context__` is set to `True` on it.
- Raising inside an `except` block *without* `from` still records the
  original, on `__context__`. The traceback then says "During handling of the
  above exception, another exception occurred", which suggests the second
  error was an accident while dealing with the first. `from e` says the
  translation was deliberate.

## Notes

Sometimes you do not want to replace an exception, only to add context to it
as it passes up: which row of a file, which user, which request. Since
Python 3.11, `add_note(text)` attaches extra lines that are printed under the
exception's message in the traceback, and a bare `raise` re-raises the very
same exception object:

```python
try:
    process(row)
except ValueError as e:
    e.add_note(f"while processing row {i}")
    raise
```

```pycon
>>> try:
...     try:
...         int("x")
...     except ValueError as e:
...         e.add_note("while processing row 7")
...         raise
... except ValueError as e:
...     print(e.__notes__)
...
['while processing row 7']
```

The notes are stored as a list in `__notes__`. The exception's type and
message are unchanged, so callers that catch `ValueError` still work.

## ExceptionGroup and except*

Sometimes several independent things fail at once: three fields of a form
are invalid, or two of five concurrent downloads failed. Raising only the
first error hides the others, and the user fixes one problem only to be told
about the next. `ExceptionGroup` (3.11+) carries them together, as one
exception holding a list:

```python
errors = []
for field in fields:
    try:
        validate(field)
    except ValueError as e:
        errors.append(e)
if errors:
    raise ExceptionGroup("invalid form", errors)
```

The group has a message of its own and an `exceptions` attribute with the
list. To handle a group, use `except*` (with a star) instead of `except`.
Each `except*` handles the matching **part** of a group: it receives a smaller
group containing only the exceptions of its type, while everything else
continues to the next `except*`. Whatever is left unhandled is re-raised:

```python
try:
    run_all()
except* ValueError as group:
    print(len(group.exceptions), "bad values")
except* OSError as group:
    print("I/O problems:", group.exceptions)
```

```pycon
>>> try:
...     raise ExceptionGroup("several", [ValueError("a"), KeyError("b"), ValueError("c")])
... except* ValueError as group:
...     print("values:", len(group.exceptions))
... except* KeyError as group:
...     print("keys:", len(group.exceptions))
...
values: 2
keys: 1
```

Unlike ordinary `except`, *several* `except*` clauses can run for one
group, one per type present. `asyncio.TaskGroup`, from the asyncio lesson,
raises exactly this kind of group when tasks fail.

## else and finally

A full `try` statement has four parts:

```python
try:
    conn = connect()
except OSError:
    log("could not connect")
else:
    use(conn)            # only if connect() did not raise; exceptions here are not caught above
finally:
    cleanup()            # always, even after return or an uncaught exception
```

Why put `use(conn)` in `else` rather than at the end of the `try` block?
Because then an `OSError` raised by `use` itself is *not* caught by the
`except` above, which is only meant for connection failures. A mistake in
`use` should surface as itself, not be reported as "could not connect".

That is the general rule: keep the `try` block as small as possible, ideally
one operation, so you only catch the errors you meant to. `finally` runs no
matter how the statement is left: normally, by an exception, or even by a
`return` inside the `try`.

## Your turn

In `errors.py`:

- `AppError(Exception)`, `ConfigError(AppError)`, and
  `NetworkError(AppError)`, whose `__init__(message, retryable)` stores
  `retryable` as an attribute and keeps the message, so
  `str(NetworkError("down", retryable=True))` is `"down"`.
- `load_port(raw)`: return `int(raw["port"])` if it is between 1 and 65535
  inclusive (the value may be a string such as `"8080"` or already an `int`).
  A missing key or a value that is not a number raises `ConfigError`
  **chained from** the original `KeyError` or `ValueError`; an out-of-range
  number raises `ConfigError` with no cause (`from None`).
- `with_row_note(func, rows)`: call `func(row)` for each row; if it raises,
  add the note `"row <index>"` (the position in `rows`, from 0) to the
  exception and re-raise it unchanged.
- `validate_all(records)`: each record is a dict that needs an `"id"` key
  (`KeyError` if missing) and a non-negative `"qty"` (`ValueError` if
  negative). Check every record for both problems, so a record with neither
  an id nor a valid quantity contributes two errors. Raise one
  `ExceptionGroup("validation failed", [...])` with every problem, or return
  `True` if there are none.
- `count_by_kind(records)`: call `validate_all` and use `except*` (a test
  checks the source contains it) to return
  `{"key": <number of KeyErrors>, "value": <number of ValueErrors>}`; both
  are `0` when the records are all valid.
