def second_largest(numbers):
    distinct = sorted(set(numbers))
    if len(distinct) < 2:
        return None
    return distinct[-2]


def chunk(items, size):
    return [items[start:start + size] for start in range(0, len(items), size)]


def rotate(items, k):
    if not items:
        return []
    k %= len(items)
    if k == 0:
        return list(items)
    return items[-k:] + items[:-k]


def bounding_box(points):
    xs = [x for x, _ in points]
    ys = [y for _, y in points]
    return (min(xs), min(ys)), (max(xs), max(ys))
