---
title: Structured logging and context
summary: Configure the logging module properly, emit JSON lines, and attach a request id to every log line with contextvars, even across async tasks.
order: 8
files: [obs.py]
run: python obs.py
hints:
  - "`request_id = contextvars.ContextVar(\"request_id\", default=None)`. `bind_request_id(value)` is a `@contextmanager`: `token = request_id.set(value)`, `try: yield`, `finally: request_id.reset(token)`."
  - "`RequestIdFilter.filter(self, record)`: `record.request_id = request_id.get()` and `return True`. Filters can add attributes as well as drop records."
  - "`JsonFormatter.format(record)`: build a dict with `ts` (`datetime.fromtimestamp(record.created, timezone.utc).isoformat()`), `level` (`record.levelname.lower()`), `logger`, `msg` (`record.getMessage()`), `request_id`, add `record.__dict__.get(\"extra_fields\", {})`, and `json.dumps` it."
  - "`setup_logging(stream)`: `logger = logging.getLogger(\"app\")`, remove old handlers, add a `StreamHandler(stream)` with the formatter and filter, `setLevel(logging.INFO)`, `propagate = False`, return it."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **log** | the record a program writes of what it did |
| **structured log** | each line a set of named fields a machine can search, not free text |
| **log level** | how important a line is: `DEBUG < INFO < WARNING < ERROR < CRITICAL` |
| **logger** | what code logs to; named in a dotted hierarchy (`app.db` is a child of `app`) |
| **root logger** | the top of the hierarchy |
| **propagate** | hand records on to the parent logger too |
| **handler** | decides where records go: a stream, a file, a rotating file |
| **formatter** | turns a record into text |
| **filter** | runs before a record is handled; can drop it or add fields |
| **`LogRecord`** | the object holding one message with its level, time and logger name |
| **lazy formatting** | `%s` placeholders filled only if the level is on |
| **JSON lines** | one JSON object per line |
| **ISO 8601** | the time format `2026-09-18T01:20:56+00:00`; `+00:00` is UTC |
| **UTC** | the world's reference time zone; log in it so machines line up |
| **request id** | a tag on every line of one request, to follow it through the log |
| **context** | where a `ContextVar` holds its value; each asyncio task runs in a copy |
| **token** | what `ContextVar.set` returns, remembering the previous value |
| **thread-local storage** | the older per-thread tool, which does not work for async tasks sharing a thread |

### Python names and functions

| Name | What it does |
|---|---|
| `logging.getLogger(name)` | the logger of that name (`__name__` for the module) |
| `log.debug/info/warning/error(msg, *args)` | log at that level; `%%` is a literal percent |
| `log.exception(msg)` | ERROR plus the current traceback, inside `except` |
| `logging.StreamHandler(stream)`, `FileHandler`, `RotatingFileHandler` | write to a stream; a file; a file restarted when big |
| `handler.setFormatter(f)`, `handler.addFilter(f)` | attach a formatter; a filter |
| `log.addHandler(h)`, `log.removeHandler(h)`, `log.handlers` | add, remove, list handlers |
| `log.setLevel(logging.INFO)`, `log.propagate = False` | set the level; stop passing to the parent |
| `logging.Formatter("%(levelname)s %(name)s: %(message)s")` | a text format with record fields |
| `logging.Filter` subclass, `filter(record)` | return `True` to keep the record |
| `record.getMessage()`, `record.levelname`, `record.created`, `record.name` | the message with arguments filled in; level name; time as a number; logger name |
| `extra={"extra_fields": {...}}` | puts extra attributes on the record |
| `datetime.fromtimestamp(t, timezone.utc).isoformat()` | a time as UTC ISO 8601 |
| `io.StringIO()`, `stream.getvalue()` | a file-like object writing into a string; its contents |
| `contextvars.ContextVar("name", default=None)` | a context variable |
| `var.set(value)`, `var.get()`, `var.reset(token)` | change it (returning a token); read it; restore the previous value |
| `@contextmanager` with `try: yield` / `finally:` | sets and restores a value around a block |
| `json.dumps(d)` | one line of JSON |
| `asyncio.gather`, `asyncio.sleep` | run the simulated requests concurrently |

---

`print` is fine for scripts. A service that runs for weeks and handles
thousands of requests needs something better. When it misbehaves at 3 a.m.,
the log is often the only record of what happened, and nobody reads millions
of lines by eye. Logs need to be ones a machine can search: **structured**
(each line a set of named fields, not free text), **levelled** (so routine
chatter can be filtered out and errors found fast), and tagged with enough
context, such as a request id, to follow one request through many lines from
many functions.

## The logging module in one screen

```python
import logging

log = logging.getLogger(__name__)      # a named logger per module
log.info("user %s logged in", user_id) # lazy %-formatting: skipped if the level is off
log.warning("disk at %d%%", pct)
log.exception("payment failed")        # ERROR plus the current traceback
```

(A sketch: `user_id` and `pct` stand for real values.)

`getLogger(__name__)` gives each module its own logger, named after the
module, such as `app.db`. The message is written with `%s` placeholders and
the values passed separately, instead of an f-string. That is deliberate: if
the level is switched off, the message is never built at all, which saves
work for messages logged in hot code. (`%%` is a literal percent sign.)
`log.exception(...)` is for use inside an `except` block: it logs at ERROR
level and adds the traceback of the exception being handled.

The pieces:

- **Loggers** (`getLogger("app.db")`) are what code logs to. Their names form
  a dotted hierarchy: `app.db` is a child of `app`, which is a child of the
  **root logger**. A logger hands each record on to its parent too, unless
  its `propagate` attribute is `False`.
- **Handlers** decide where records go: `StreamHandler` (a stream such as the
  terminal), `FileHandler` (a file), `RotatingFileHandler` (a file that is
  renamed and restarted when it gets big)... A logger can have several.
- **Formatters** turn a `LogRecord` (the object holding a message, its level,
  time, logger name and so on) into text. Each handler has one.
- **Filters** run before a record is handled. They can drop records, or
  **add fields** to them; this lesson uses one for the second job.
- **Levels**: `DEBUG < INFO < WARNING < ERROR < CRITICAL`. Set on a logger or
  a handler, a level passes that level and anything more severe, and drops
  the rest: at INFO, `debug()` calls produce nothing.

```pycon
>>> import io, logging
>>> stream = io.StringIO()                       # a stream in memory, for the demo
>>> handler = logging.StreamHandler(stream)
>>> handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
>>> log = logging.getLogger("demo")
>>> log.addHandler(handler)
>>> log.setLevel(logging.INFO)
>>> log.propagate = False
>>> log.debug("too detailed")                    # below INFO: dropped
>>> log.info("user %s logged in", "ana")
>>> log.warning("disk at %d%%", 91)
>>> print(stream.getvalue(), end="")
INFO demo: user ana logged in
WARNING demo: disk at 91%
```

(`io.StringIO` is a file-like object that writes into a string, so the
example can show exactly what the handler wrote.)

Libraries should only call `getLogger(__name__)` and log. Configuring
handlers, formats and levels is the **application's** job, done once at
start-up, because only the application knows where its logs should go. A
library that adds its own handler forces its choices on everyone who uses
it.

## Structured: JSON lines

A line like `user ana logged in` is easy for a person to read and hard for a
program to search: is "ana" a user name or part of the message? **JSON
lines**, one JSON object per line, keep each piece of information in its own
named field. They can be shipped to a log store, indexed and queried ("every
error for request r-17", "every request to /api/search slower than a
second"). This is what the homelab monitoring contract expects from
services:

```json
{"ts": "2026-09-18T01:20:56+00:00", "level": "error", "logger": "app", "msg": "upstream timeout", "request_id": "r-17", "route": "/api/search"}
```

`ts` is the time in **ISO 8601** format, the international standard
`year-month-dayThour:minute:second`, with `+00:00` meaning UTC. Always log in
UTC, so lines from machines in different time zones line up.

`extra={...}` on a logging call puts extra attributes on the record, which a
custom formatter can include. This lesson's convention is to put them all
under one key, `extra={"extra_fields": {"route": "/login"}}`, so the
formatter knows exactly which attributes to copy into the JSON.

## contextvars: context without passing it around

To tag every line of a request with its id, every function that logs needs
the id. Threading a `request_id` argument through every function, only to
log it, is miserable, and a global variable would be wrong as soon as two
requests run at once. A `ContextVar` (from the `contextvars` module) holds a
value for the **current context**:

```python
import contextvars

request_id = contextvars.ContextVar("request_id", default=None)

token = request_id.set("r-17")
try:
    handle()                 # anything here, however deep, sees "r-17"
finally:
    request_id.reset(token)
```

`set(value)` changes the value and returns a **token** that remembers the
previous one; `reset(token)` puts the previous value back. `get()` reads the
current value, or the default. Wrapping `set` and `reset` in `try`/`finally`
(or in a context manager) guarantees the old value comes back even if the
code in between raises.

Unlike a global, each `asyncio` task runs in a **copy** of the context, taken
when the task is created, so two concurrent requests each see their own id:

```pycon
>>> import asyncio, contextvars
>>> current = contextvars.ContextVar("current", default=None)
>>> async def handle(name, delay):
...     current.set(name)                 # only changes this task's copy
...     await asyncio.sleep(delay)        # the other task runs meanwhile
...     return f"{name} sees {current.get()}"
...
>>> async def main():
...     return await asyncio.gather(handle("a", 0.02), handle("b", 0.01))
...
>>> asyncio.run(main())
['a sees a', 'b sees b']
```

Task `b` set its value while `a` was sleeping, and `a` still saw its own.
(Thread-local storage, the older tool for per-thread values, cannot do that
for async code, because all tasks share one thread.)

## Putting it together

The design that falls out of this:

1. The request handler binds the request id in a `ContextVar` once, at the
   start of the request.
2. A **filter** on the handler reads the context variable and attaches it to
   every record as `record.request_id`. A filter's `filter(record)` method
   returns `True` to keep the record, so one that only adds a field always
   returns `True`.
3. The **formatter** writes each record as one line of JSON.

Application code only calls `log.info(...)`, and every line comes out
structured and tagged, without any function having to know about request ids.

## Your turn

In `obs.py` (the starter's `handle` and `main` simulate three concurrent
requests; press **Run** to see their log lines):

- `request_id`: a `ContextVar` named `"request_id"`, defaulting to `None`.
- `bind_request_id(value)`: a context manager (use `@contextmanager`) setting
  it for the duration of a block and restoring the previous value afterwards,
  also when the block raises. Nested blocks restore the outer value.
- `RequestIdFilter`: a `logging.Filter` subclass whose `filter(record)` adds
  `record.request_id` from the context variable and keeps every record.
- `JsonFormatter`: a `logging.Formatter` subclass whose `format(record)`
  returns one JSON object with the keys `ts` (the record's time, as UTC ISO
  8601), `level` (lower-case, such as `"info"`), `logger` (the logger's name),
  `msg` (the message with its `%s` arguments filled in, from
  `record.getMessage()`), `request_id`, plus every key passed as
  `extra={"extra_fields": {...}}`.
- `setup_logging(stream)`: configure and return the `"app"` logger at INFO,
  writing JSON to `stream` with the filter. Calling it twice must leave
  exactly one handler (remove the old ones first), and the logger must not
  propagate to the root logger.

Each concurrent request's lines must carry its own id: the test runs the
three simulated requests at once and checks every `done` line.
