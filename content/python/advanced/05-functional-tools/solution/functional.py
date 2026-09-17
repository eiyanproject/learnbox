import functools
import operator


def compose(*funcs):
    return functools.reduce(lambda f, g: lambda x: g(f(x)), funcs, lambda x: x)


parse_bits = functools.partial(int, base=2)


@functools.singledispatch
def to_json_like(value):
    raise TypeError(f"cannot convert {type(value).__name__}")


@to_json_like.register
def _(value: dict):
    items = ", ".join(f"{to_json_like(str(k))}: {to_json_like(v)}" for k, v in sorted(value.items()))
    return "{" + items + "}"


@to_json_like.register
def _(value: list):
    return "[" + ", ".join(to_json_like(v) for v in value) + "]"


@to_json_like.register
def _(value: str):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


@to_json_like.register(int)
@to_json_like.register(float)
def _(value):
    return repr(value)


@to_json_like.register
def _(value: bool):
    return "true" if value else "false"


@to_json_like.register(type(None))
def _(value):
    return "null"


def by_fields(*names):
    return operator.attrgetter(*names)


class Report:
    def __init__(self, rows):
        self.rows = rows
        self.computations = 0

    @functools.cached_property
    def summary(self):
        self.computations += 1
        return {"count": len(self.rows), "total": sum(self.rows)}
