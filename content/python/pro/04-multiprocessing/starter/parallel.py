import math
import time
from concurrent.futures import ProcessPoolExecutor


def is_prime(n):
    pass


def count_primes_in_range(bounds):
    pass


def split_range(start, stop, parts):
    pass


def parallel_prime_count(start, stop, workers=2):
    pass


def map_with_errors(func, items, workers=2):
    pass


if __name__ == "__main__":
    t = time.perf_counter()
    print("serial:  ", count_primes_in_range((0, 300_000)), f"{time.perf_counter() - t:.2f}s")
    t = time.perf_counter()
    print("parallel:", parallel_prime_count(0, 300_000), f"{time.perf_counter() - t:.2f}s")
