import queue
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch_all(urls, fetch, max_workers=8):
    with ThreadPoolExecutor(max_workers) as pool:
        return list(pool.map(fetch, urls))


class Counter:
    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            current = self.value
            self.value = current + 1


def first_success(funcs):
    with ThreadPoolExecutor(max(1, len(funcs))) as pool:
        futures = [pool.submit(f) for f in funcs]
        for fut in as_completed(futures):
            try:
                return fut.result()
            except Exception:
                continue
    raise RuntimeError("every function failed")


def worker_pipeline(items, process, n_workers):
    q = queue.Queue()
    out = []
    out_lock = threading.Lock()

    def worker():
        while (item := q.get()) is not None:
            result = process(item)
            with out_lock:
                out.append(result)

    threads = [threading.Thread(target=worker) for _ in range(n_workers)]
    for t in threads:
        t.start()
    for item in items:
        q.put(item)
    for _ in threads:
        q.put(None)
    for t in threads:
        t.join()
    return sorted(out)
