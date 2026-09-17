import functools


def primed(genfunc):
    @functools.wraps(genfunc)
    def start(*args, **kwargs):
        gen = genfunc(*args, **kwargs)
        next(gen)
        return gen

    return start


@primed
def running_average():
    total = count = 0
    average = None
    while True:
        value = yield average
        total += value
        count += 1
        average = total / count


def accumulate_until_none():
    total = 0
    while True:
        value = yield
        if value is None:
            return total
        total += value


@primed
def batch_totals(results):
    """Send numbers; send None to close a batch. Each batch total is appended to results."""
    while True:
        total = yield from accumulate_until_none()
        results.append(total)
