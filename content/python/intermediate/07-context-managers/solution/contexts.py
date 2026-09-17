import os
import time
from contextlib import contextmanager


class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.elapsed = time.perf_counter() - self.start
        return False


@contextmanager
def changed_dir(path):
    old = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


@contextmanager
def ignore_errors(*exception_types):
    try:
        yield
    except exception_types:
        pass


class Transaction:
    def __init__(self, data):
        self.data = data

    def __enter__(self):
        self.working = dict(self.data)
        return self.working

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.data.clear()
            self.data.update(self.working)
        return False
