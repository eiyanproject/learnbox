import asyncio


async def fetch_all(urls, fetch):
    return await asyncio.gather(*(fetch(u) for u in urls))


async def fetch_with_timeout(coro, timeout, default=None):
    try:
        return await asyncio.wait_for(coro, timeout)
    except TimeoutError:
        return default


async def limited_gather(urls, fetch, limit):
    sem = asyncio.Semaphore(limit)

    async def one(u):
        async with sem:
            return await fetch(u)

    return await asyncio.gather(*(one(u) for u in urls))


async def ticker(n, delay):
    for i in range(n):
        await asyncio.sleep(delay)
        yield i


async def collect(agen):
    return [x async for x in agen]
