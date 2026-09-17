import asyncio


async def fetch_all(urls, fetch):
    results = []
    for u in urls:
        results.append(await fetch(u))  # correct, but one at a time
    return results


async def fetch_with_timeout(coro, timeout, default=None):
    pass


async def limited_gather(urls, fetch, limit):
    pass


async def ticker(n, delay):
    pass


async def collect(agen):
    pass
