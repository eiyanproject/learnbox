import inspect
import os

from helpers_for_parallel import inverse, pid_of
from parallel import count_primes_in_range, is_prime, map_with_errors, parallel_prime_count, split_range


def test_is_prime():
    assert [n for n in range(30) if is_prime(n)] == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    assert is_prime(7919) and not is_prime(7917)


def test_count_primes_in_range():
    assert count_primes_in_range((0, 100)) == 25
    assert count_primes_in_range((100, 200)) == 21
    assert count_primes_in_range((5, 5)) == 0


def test_split_range_covers_exactly():
    chunks = split_range(0, 10, 3)
    assert chunks == [(0, 4), (4, 8), (8, 10)]
    assert split_range(10, 13, 8) == [(10, 11), (11, 12), (12, 13)]
    assert split_range(0, 0, 4) == []


def test_split_range_no_gaps_or_overlaps():
    chunks = split_range(7, 1001, 6)
    assert len(chunks) <= 6
    assert chunks[0][0] == 7 and chunks[-1][1] == 1001
    assert all(a[1] == b[0] for a, b in zip(chunks, chunks[1:]))


def test_parallel_prime_count_matches_serial():
    assert parallel_prime_count(0, 50_000, workers=2) == count_primes_in_range((0, 50_000)) == 5133


def test_parallel_uses_process_pool():
    source = inspect.getsource(parallel_prime_count)
    assert "ProcessPoolExecutor" in source


def test_map_with_errors_order_and_errors():
    assert map_with_errors(inverse, [1, 0, 4], workers=2) == [("ok", 1.0), ("error", "ZeroDivisionError"), ("ok", 0.25)]


def test_work_runs_in_other_processes():
    results = map_with_errors(pid_of, range(4), workers=2)
    pids = {value for status, value in results}
    assert all(status == "ok" for status, _ in results)
    assert os.getpid() not in pids
