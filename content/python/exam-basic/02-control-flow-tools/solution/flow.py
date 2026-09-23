def first_divisible(values, divisor):
    for value in values:
        if value % divisor == 0:
            return value
    else:
        return "none"


def append_safely(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target


def describe_args(*args, **kwargs):
    return {
        "count": len(args),
        "names": sorted(kwargs),
        "total": sum(args),
    }


def apply_all(funcs, value):
    for func in funcs:
        value = func(value)
    return value
