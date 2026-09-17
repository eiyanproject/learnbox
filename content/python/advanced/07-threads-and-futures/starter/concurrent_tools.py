import queue
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch_all(urls, fetch, max_workers=8):
    return [fetch(u) for u in urls]  # correct, but one at a time


class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        current = self.value
        self.value = current + 1


def first_success(funcs):
    pass


def worker_pipeline(items, process, n_workers):
    pass
