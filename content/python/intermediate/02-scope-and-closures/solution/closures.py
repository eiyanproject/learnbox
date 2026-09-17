def make_counter(start=0):
    count = start

    def increment():
        nonlocal count
        count += 1
        return count

    return increment


def make_multiplier(n):
    return lambda x: x * n


def make_accumulator():
    values = []

    def add(x):
        values.append(x)
        return sum(values) / len(values)

    return add


def make_adders(n):
    return [lambda x, i=i: x + i for i in range(n)]
