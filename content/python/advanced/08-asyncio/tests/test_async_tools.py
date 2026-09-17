import asyncio
import inspect
import time

from async_tools import collect, fetch_all, fetch_with_timeout, limited_gather, ticker


async def slow_upper(s, delay=0.2):
    await asyncio.sleep(delay)
    return s.upper()


def test_fetch_all_concurrent_and_ordered():
    urls = [f"u{i}" for i in range(20)]
    start = time.perf_counter()
    result = asyncio.run(fetch_all(urls, slow_upper))
    assert list(result) == [u.upper() for u in urls]
    assert time.perf_counter() - start < 1, "20 x 0.2s one at a time would take 4s"


def test_fetch_with_timeout_ok():
    assert asyncio.run(fetch_with_timeout(slow_upper("a", 0.01), 1)) == "A"


def test_fetch_with_timeout_default():
    start = time.perf_counter()
    assert asyncio.run(fetch_with_timeout(slow_upper("a", 5), 0.1, default="late")) == "late"
    assert time.perf_counter() - start < 1


def test_limited_gather_respects_limit():
    running = 0
    peak = 0

    async def tracked(u):
        nonlocal running, peak
        running += 1
        peak = max(peak, running)
        await asyncio.sleep(0.05)
        running -= 1
        return u * 2

    result = asyncio.run(limited_gather(list(range(12)), tracked, 3))
    assert list(result) == [u * 2 for u in range(12)]
    assert peak == 3


def test_ticker_is_async_generator():
    assert inspect.isasyncgenfunction(ticker)
    start = time.perf_counter()
    assert asyncio.run(collect(ticker(3, 0.05))) == [0, 1, 2]
    assert time.perf_counter() - start >= 0.14


def test_collect_any_async_iterable():
    class Countdown:
        def __init__(self, n):
            self.n = n

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.n == 0:
                raise StopAsyncIteration
            self.n -= 1
            return self.n + 1

    assert asyncio.run(collect(Countdown(3))) == [3, 2, 1]
