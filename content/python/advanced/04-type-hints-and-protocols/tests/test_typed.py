import inspect
import typing

import pytest

import typed
from typed import Config, Stack, SupportsArea, first, parse_config, total_area


def fully_annotated(func):
    sig = inspect.signature(func)
    params = [p for name, p in sig.parameters.items() if name != "self"]
    return all(p.annotation is not inspect.Parameter.empty for p in params) and (
        sig.return_annotation is not inspect.Signature.empty
    )


def test_first():
    assert first([3, 2]) == 3
    assert first("xy") == "x"
    assert first([]) is None


def test_first_is_generic():
    hints = typing.get_type_hints(first)
    assert isinstance(hints["items"].__args__[0], typing.TypeVar)


def test_stack():
    s: Stack[int] = Stack()
    assert len(s) == 0 and s.peek() is None
    s.push(1)
    s.push(2)
    assert s.peek() == 2 and len(s) == 2
    assert s.pop() == 2 and s.pop() == 1
    with pytest.raises(IndexError):
        s.pop()


def test_stack_is_generic():
    assert typing.Generic in Stack.__mro__
    assert Stack[str] is not None


def test_protocol_is_structural():
    class Square:
        def __init__(self, side):
            self.side = side

        def area(self) -> float:
            return self.side**2

    class NoArea:
        pass

    assert isinstance(Square(2), SupportsArea)
    assert not isinstance(NoArea(), SupportsArea)
    assert typing.Protocol in SupportsArea.__mro__
    assert total_area([Square(2), Square(3)]) == 13
    assert total_area([]) == 0


def test_config_typed_dict():
    assert typing.is_typeddict(Config)
    assert typing.get_type_hints(Config) == {"host": str, "port": int, "debug": bool}


def test_parse_config():
    assert parse_config({"host": "db", "port": "5432", "debug": "Yes"}) == {"host": "db", "port": 5432, "debug": True}
    assert parse_config({"host": "x", "port": "80", "debug": "no"})["debug"] is False
    assert parse_config({"host": "x", "port": "80"})["debug"] is False


def test_everything_is_annotated():
    for func in (first, total_area, parse_config, Stack.push, Stack.pop, Stack.peek, Stack.__len__):
        assert fully_annotated(func), f"{func.__qualname__} is missing annotations"
    assert typed.__name__ == "typed"
