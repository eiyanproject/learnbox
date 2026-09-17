import itertools


def countdown(n):
    while n > 0:
        yield n
        n -= 1


def read_records(lines):
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        yield line.split(",")


def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def take(n, iterable):
    return list(itertools.islice(iterable, n))


def chunked(iterable, size):
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
