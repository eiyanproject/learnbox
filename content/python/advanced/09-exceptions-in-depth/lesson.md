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

## Design an exception hierarchy

Libraries define a base exception so callers can catch "anything from this
library" or something specific:

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

Subclass `Exception`, not `BaseException` (that also covers `KeyboardInterrupt`
and `SystemExit`). Put useful data in attributes, not only in the message.

## Chaining: raise ... from

Translate a low-level error into your own without losing the cause:

```python
try:
    port = int(config["port"])
except (KeyError, ValueError) as e:
    raise ConfigError("port missing or not a number") from e
```

The traceback then shows both, joined by "The above exception was the direct
cause of the following exception". The original is on `err.__cause__`.

`raise NewError() from None` hides the cause when it would only be noise.
Raising inside an `except` block without `from` still records the original, on
`__context__` ("During handling of the above exception, another exception occurred").

## Notes

Add context as an exception passes up, without wrapping it:

```python
try:
    process(row)
except ValueError as e:
    e.add_note(f"while processing row {i}")
    raise
```

## ExceptionGroup and except*

Sometimes several independent things fail at once (validating a form, running
concurrent tasks). `ExceptionGroup` carries them together:

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

`except*` handles the matching **part** of a group; everything else continues
to the next `except*`, and whatever is left unhandled is re-raised:

```python
try:
    run_all()
except* ValueError as group:
    print(len(group.exceptions), "bad values")
except* OSError as group:
    print("I/O problems:", group.exceptions)
```

`asyncio.TaskGroup` raises exactly this kind of group when tasks fail.

## else and finally

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

Keep the `try` block as small as possible so you only catch the errors you meant to.

## Your turn

In `errors.py`:

- `AppError(Exception)`, `ConfigError(AppError)`, and
  `NetworkError(AppError)` whose `__init__(message, retryable)` stores `retryable`
- `load_port(raw)`: return `int(raw["port"])` if it is between 1 and 65535;
  a missing key or non-number raises `ConfigError` **chained from** the
  original; an out-of-range number raises `ConfigError` with no cause
  (`from None`)
- `with_row_note(func, rows)`: call `func(row)` for each row; if it raises,
  add the note `"row <index>"` to the exception and re-raise it unchanged
- `validate_all(records)`: each record is a dict that needs an `"id"` key
  (`KeyError` if missing) and a non-negative `"qty"` (`ValueError` if negative).
  Raise one `ExceptionGroup("validation failed", [...])` with every problem, or return `True`.
- `count_by_kind(records)`: use `except*` to return
  `{"key": <number of KeyErrors>, "value": <number of ValueErrors>}`
