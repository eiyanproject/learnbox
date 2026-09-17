import asyncio
import contextvars
import json
import logging
import sys
from contextlib import contextmanager
from datetime import datetime, timezone

request_id = None


def bind_request_id(value):
    pass


class RequestIdFilter(logging.Filter):
    pass


class JsonFormatter(logging.Formatter):
    pass


def setup_logging(stream):
    pass


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
