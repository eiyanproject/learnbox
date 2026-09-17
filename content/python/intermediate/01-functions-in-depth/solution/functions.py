def total(*numbers, start=0):
    return start + sum(numbers)


def describe(name, **attributes):
    if not attributes:
        return name
    parts = ", ".join(f"{key}={attributes[key]}" for key in sorted(attributes))
    return f"{name} ({parts})"


def make_tag(tag, text, *, cls=None, id=None):
    attrs = ""
    if cls is not None:
        attrs += f' class="{cls}"'
    if id is not None:
        attrs += f' id="{id}"'
    return f"<{tag}{attrs}>{text}</{tag}>"


def apply_all(funcs, value):
    return [f(value) for f in funcs]


def sort_people(people):
    return sorted(people, key=lambda p: (-p[1], p[0]))
