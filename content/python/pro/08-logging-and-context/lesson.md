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

`print` is fine for scripts. Services need logs that a machine can search:
structured, levelled, and tagged with enough context to follow one request
through many lines.

## The logging module in one screen

```python
import logging

log = logging.getLogger(__name__)      # a named logger per module
log.info("user %s logged in", user_id) # lazy %-formatting: skipped if the level is off
log.warning("disk at %d%%", pct)
log.exception("payment failed")        # ERROR plus the current traceback
```

The pieces:

- **Loggers** (`getLogger("app.db")`) form a dotted hierarchy and pass records
  up to their parents (`propagate`).
- **Handlers** decide where records go: `StreamHandler`, `FileHandler`,
  `RotatingFileHandler`...
- **Formatters** turn a `LogRecord` into text.
- **Filters** drop records or **add fields** to them.
- **Levels**: `DEBUG < INFO < WARNING < ERROR < CRITICAL`, set on loggers and handlers.

Libraries should only call `getLogger(__name__)` and log. Configuring handlers
is the **application's** job, done once at start-up.

## Structured: JSON lines

One JSON object per line can be shipped, indexed and queried (this is what the
homelab monitoring contract expects from services):

```json
{"ts": "2026-09-18T01:20:56+00:00", "level": "error", "logger": "app", "msg": "upstream timeout", "request_id": "r-17", "route": "/api/search"}
```

`extra={...}` on a logging call puts extra attributes on the record, which a
custom formatter can include.

## contextvars: context without passing it around

Threading a `request_id` argument through every function just to log it is
miserable. A `ContextVar` holds a value for the **current context**:

```python
import contextvars

request_id = contextvars.ContextVar("request_id", default=None)

token = request_id.set("r-17")
try:
    handle()                 # anything here, however deep, sees "r-17"
finally:
    request_id.reset(token)
```

Unlike a global, each `asyncio` task runs in a **copy** of the context, so two
concurrent requests each see their own id. (Thread-local storage cannot do that
for async code, because all tasks share one thread.)

## Putting it together

A **filter** reads the context variable and attaches it to every record; the
**formatter** writes JSON. Application code just calls `log.info(...)`.

## Your turn

In `obs.py`:

- `request_id`: a `ContextVar` defaulting to `None`
- `bind_request_id(value)`: a context manager setting it for the duration of a
  block and restoring the previous value afterwards
- `RequestIdFilter`: a `logging.Filter` adding `record.request_id`
- `JsonFormatter`: a `logging.Formatter` producing one JSON object with keys
  `ts` (UTC ISO 8601), `level` (lower-case), `logger`, `msg`, `request_id`, plus
  anything passed as `extra={"extra_fields": {...}}`
- `setup_logging(stream)`: configure and return the `"app"` logger at INFO,
  writing JSON to `stream` with the filter, without duplicating handlers when
  called twice, and not propagating to the root logger
