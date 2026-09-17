import functools
import json
from types import SimpleNamespace

import pytest

from functional import Report, by_fields, compose, parse_bits, to_json_like


def test_compose_left_to_right():
    f = compose(lambda x: x + 1, lambda x: x * 10, str)
    assert f(1) == "20"
    assert compose()(42) == 42


def test_parse_bits_is_partial():
    assert isinstance(parse_bits, functools.partial)
    assert parse_bits("1010") == 10
    assert parse_bits("11111111") == 255


def test_to_json_like_is_singledispatch():
    assert hasattr(to_json_like, "register") and hasattr(to_json_like, "dispatch")


def test_to_json_like_scalars():
    assert to_json_like(3) == "3"
    assert to_json_like(2.5) == "2.5"
    assert to_json_like("hi") == '"hi"'
    assert to_json_like(True) == "true"
    assert to_json_like(False) == "false"
    assert to_json_like(None) == "null"


def test_to_json_like_nested_is_valid_json():
    value = {"b": [1, "two", None], "a": {"ok": True}}
    text = to_json_like(value)
    assert text.startswith('{"a"')
    assert json.loads(text) == value


def test_to_json_like_rejects_unknown():
    with pytest.raises(TypeError):
        to_json_like({1, 2})


def test_by_fields():
    people = [
        SimpleNamespace(last="Wijaya", first="Budi"),
        SimpleNamespace(last="Santoso", first="Ana"),
        SimpleNamespace(last="Wijaya", first="Ana"),
    ]
    ordered = sorted(people, key=by_fields("last", "first"))
    assert [(p.last, p.first) for p in ordered] == [("Santoso", "Ana"), ("Wijaya", "Ana"), ("Wijaya", "Budi")]


def test_report_caches():
    r = Report([3, 4, 5])
    assert r.summary == {"count": 3, "total": 12}
    assert r.summary is r.summary
    assert r.computations == 1
    del r.summary
    r.summary
    assert r.computations == 2


def test_report_uses_cached_property():
    assert isinstance(Report.__dict__["summary"], functools.cached_property)
