import asyncio
import contextvars
import json
import logging
import sys
from contextlib import contextmanager
from datetime import datetime, timezone

request_id = contextvars.ContextVar("request_id", default=None)


@contextmanager
def bind_request_id(value):
    token = request_id.set(value)
    try:
        yield
    finally:
        request_id.reset(token)


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id.get()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record):
        data = {
            "ts": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
        }
        data.update(record.__dict__.get("extra_fields", {}))
        return json.dumps(data)


def setup_logging(stream):
    logger = logging.getLogger("app")
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestIdFilter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


async def handle(n):
    log = logging.getLogger("app")
    with bind_request_id(f"req-{n}"):
        log.info("start")
        await asyncio.sleep(0.01 * (3 - n))
        log.info("done", extra={"extra_fields": {"n": n}})


async def main():
    await asyncio.gather(*(handle(i) for i in range(3)))


if __name__ == "__main__":
    setup_logging(sys.stdout)
    asyncio.run(main())
