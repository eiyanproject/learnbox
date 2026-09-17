import math
import time
from concurrent.futures import ProcessPoolExecutor


def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    for d in range(3, math.isqrt(n) + 1, 2):
        if n % d == 0:
            return False
    return True


def count_primes_in_range(bounds):
    start, stop = bounds
    return sum(1 for n in range(start, stop) if is_prime(n))


def split_range(start, stop, parts):
    if stop <= start:
        return []
    step = math.ceil((stop - start) / parts)
    return [(lo, min(lo + step, stop)) for lo in range(start, stop, step)]


def parallel_prime_count(start, stop, workers=2):
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return sum(pool.map(count_primes_in_range, split_range(start, stop, workers * 4)))


def map_with_errors(func, items, workers=2):
    results = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(func, item) for item in items]
        for fut in futures:
            try:
                results.append(("ok", fut.result()))
            except Exception as e:
                results.append(("error", type(e).__name__))
    return results


if __name__ == "__main__":
    t = time.perf_counter()
    print("serial:  ", count_primes_in_range((0, 300_000)), f"{time.perf_counter() - t:.2f}s")
    t = time.perf_counter()
    print("parallel:", parallel_prime_count(0, 300_000), f"{time.perf_counter() - t:.2f}s")
