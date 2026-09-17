class Plugin:
    registry = {}

    def __init_subclass__(cls, /, name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        Plugin.registry[name or cls.__name__.lower()] = cls

    @classmethod
    def create(cls, name, *args, **kwargs):
        return Plugin.registry[name](*args, **kwargs)


def auto_repr(cls):
    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{type(self).__name__}({fields})"

    cls.__repr__ = __repr__
    return cls


def make_record(name, fields):
    fields = tuple(fields)

    def __init__(self, *args):
        if len(args) != len(fields):
            raise TypeError(f"{name} takes {len(fields)} arguments")
        for field, value in zip(fields, args):
            setattr(self, field, value)

    return type(name, (), {"__init__": __init__, "__slots__": fields})


class FinalMeta(type):
    def __new__(mcls, name, bases, ns, final=False):
        for base in bases:
            if isinstance(base, FinalMeta) and getattr(base, "_final", False):
                raise TypeError(f"{base.__name__} is final and cannot be subclassed")
        cls = super().__new__(mcls, name, bases, ns)
        cls._final = final
        return cls

    def __init__(cls, name, bases, ns, final=False):
        super().__init__(name, bases, ns)
