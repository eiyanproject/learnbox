import asyncio
import contextvars
import io
import json
import logging
from datetime import datetime

import obs


def lines(stream):
    return [json.loads(line) for line in stream.getvalue().splitlines()]


def test_request_id_var():
    assert isinstance(obs.request_id, contextvars.ContextVar)
    assert obs.request_id.get() is None


def test_bind_restores_previous_value():
    with obs.bind_request_id("outer"):
        with obs.bind_request_id("inner"):
            assert obs.request_id.get() == "inner"
        assert obs.request_id.get() == "outer"
    assert obs.request_id.get() is None


def test_bind_restores_after_exception():
    try:
        with obs.bind_request_id("x"):
            raise RuntimeError
    except RuntimeError:
        pass
    assert obs.request_id.get() is None


def test_json_lines():
    stream = io.StringIO()
    log = obs.setup_logging(stream)
    with obs.bind_request_id("r-17"):
        log.info("user %s logged in", "ana", extra={"extra_fields": {"route": "/login"}})
    log.debug("hidden")
    log.warning("no context")
    first, second = lines(stream)
    assert first["msg"] == "user ana logged in"
    assert first["level"] == "info" and first["logger"] == "app"
    assert first["request_id"] == "r-17" and first["route"] == "/login"
    assert datetime.fromisoformat(first["ts"]).utcoffset().total_seconds() == 0
    assert second == {**second, "level": "warning", "request_id": None}


def test_setup_is_idempotent_and_does_not_propagate():
    stream = io.StringIO()
    obs.setup_logging(io.StringIO())
    log = obs.setup_logging(stream)
    assert len(log.handlers) == 1
    assert log.propagate is False
    assert log.level == logging.INFO
    log.info("once")
    assert len(lines(stream)) == 1


def test_context_is_per_async_task():
    stream = io.StringIO()
    obs.setup_logging(stream)

    async def main():
        await asyncio.gather(*(obs.handle(i) for i in range(3)))

    asyncio.run(main())
    records = lines(stream)
    assert len(records) == 6
    for record in records:
        if record["msg"] == "done":
            assert record["request_id"] == f"req-{record['n']}"
    assert [r["request_id"] for r in records if r["msg"] == "done"] == ["req-2", "req-1", "req-0"]
