def first_bad(n, is_bad):
    lo, hi = 1, n + 1  # hi stands for "none of them"
    while lo < hi:
        mid = (lo + hi) // 2
        if is_bad(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo if lo <= n else None


def minimal_failing(items, fails):
    current = list(items)
    i = 0
    while i < len(current):
        without = current[:i] + current[i + 1:]
        if fails(without):
            current = without
        else:
            i += 1
    return current
