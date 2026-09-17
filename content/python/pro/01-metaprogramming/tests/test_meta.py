import pytest

from meta import FinalMeta, Plugin, auto_repr, make_record


def test_plugins_register_themselves():
    class CsvExport(Plugin, name="csv"):
        def __init__(self, sep=","):
            self.sep = sep

    class Markdown(Plugin):
        pass

    assert Plugin.registry["csv"] is CsvExport
    assert Plugin.registry["markdown"] is Markdown
    exporter = Plugin.create("csv", ";")
    assert isinstance(exporter, CsvExport) and exporter.sep == ";"


def test_unknown_plugin():
    with pytest.raises(KeyError):
        Plugin.create("nope")


def test_plugin_uses_init_subclass():
    assert "__init_subclass__" in Plugin.__dict__


def test_auto_repr():
    @auto_repr
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    assert repr(Point(1, "a")) == "Point(x=1, y='a')"


def test_auto_repr_returns_class():
    @auto_repr
    class Empty:
        pass

    assert isinstance(Empty, type)
    assert repr(Empty()) == "Empty()"


def test_make_record():
    Person = make_record("Person", ["name", "age"])
    assert Person.__name__ == "Person"
    p = Person("ana", 31)
    assert (p.name, p.age) == ("ana", 31)
    assert Person.__slots__ == ("name", "age")
    with pytest.raises(AttributeError):
        p.email = "x"


def test_make_record_argument_count():
    Pair = make_record("Pair", ["a", "b"])
    with pytest.raises(TypeError):
        Pair(1)


def test_final_classes():
    class Base(metaclass=FinalMeta):
        pass

    class Sealed(Base, final=True):
        pass

    class Child(Base):
        pass

    assert isinstance(Sealed, FinalMeta) and isinstance(Child, FinalMeta)
    with pytest.raises(TypeError):
        class Nope(Sealed):
            pass


def test_final_directly_on_root():
    class Root(metaclass=FinalMeta, final=True):
        pass

    with pytest.raises(TypeError):
        class Sub(Root):
            pass
