import sys
import threading
import time

import pytest

from concurrent_tools import Counter, fetch_all, first_success, worker_pipeline


def slow_fetch(url):
    time.sleep(0.2)
    return url.upper()


def test_fetch_all_order():
    assert fetch_all(["a", "b", "c"], str.upper) == ["A", "B", "C"]


def test_fetch_all_is_concurrent():
    urls = [f"u{i}" for i in range(16)]
    start = time.perf_counter()
    assert fetch_all(urls, slow_fetch, max_workers=16) == [u.upper() for u in urls]
    assert time.perf_counter() - start < 1.5, "16 x 0.2s sequentially would take 3.2s"


def test_counter_is_thread_safe():
    old = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)  # switch threads very often to expose races
    try:
        c = Counter()

        def hammer():
            for _ in range(20_000):
                c.increment()

        threads = [threading.Thread(target=hammer) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert c.value == 160_000
    finally:
        sys.setswitchinterval(old)


def test_first_success_returns_fastest_good_result():
    def fail_fast():
        raise ValueError

    def slow_ok():
        time.sleep(0.5)
        return "slow"

    def quick_ok():
        time.sleep(0.05)
        return "quick"

    assert first_success([fail_fast, slow_ok, quick_ok]) == "quick"


def test_first_success_all_fail():
    def boom():
        raise OSError

    with pytest.raises(RuntimeError):
        first_success([boom, boom])


def test_worker_pipeline():
    seen_threads = set()
    lock = threading.Lock()

    def process(x):
        with lock:
            seen_threads.add(threading.get_ident())
        time.sleep(0.01)
        return x * x

    assert worker_pipeline(range(40), process, 4) == sorted(x * x for x in range(40))
    assert len(seen_threads) > 1, "use several worker threads"


def test_worker_pipeline_stops_its_threads():
    before = threading.active_count()
    worker_pipeline([1, 2, 3], lambda x: x, 3)
    assert threading.active_count() == before, "send one sentinel per worker and join them"
