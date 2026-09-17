import textwrap
import typing
from pathlib import Path

import pytest

from loader import TextPlugin, discover, load_module, load_plugins, run_pipeline

HERE = Path(__file__).parent


def write(folder, name, body):
    (folder / name).write_text(textwrap.dedent(body))


def test_protocol():
    assert typing.Protocol in TextPlugin.__mro__

    class Good:
        name = "g"

        def transform(self, text):
            return text

    assert isinstance(Good(), TextPlugin)
    assert not isinstance(object(), TextPlugin)


def test_discover(tmp_path):
    for name in ["b.py", "a.py", "_private.py", "notes.txt"]:
        (tmp_path / name).write_text("")
    assert [p.name for p in discover(tmp_path)] == ["a.py", "b.py"]


def test_load_module(tmp_path):
    write(tmp_path, "answer.py", "VALUE = 6 * 7\n")
    assert load_module(tmp_path / "answer.py").VALUE == 42


def test_bundled_plugins():
    plugins, errors = load_plugins(HERE / "plugins")
    assert errors == {}
    assert set(plugins) == {"shout", "reverse"}
    assert run_pipeline("hello", plugins, ["reverse", "shout"]) == "OLLEH!"
    assert run_pipeline("abc", plugins, []) == "abc"


def test_broken_plugins_are_isolated(tmp_path):
    write(tmp_path, "good.py", """
        class P:
            name = "double"
            def transform(self, text):
                return text * 2
        plugin = P()
    """)
    write(tmp_path, "syntax.py", "def broken(:\n")
    write(tmp_path, "raises.py", "raise RuntimeError('boom at import')\n")
    write(tmp_path, "missing.py", "x = 1\n")
    write(tmp_path, "wrong.py", "plugin = 'not a plugin'\n")

    plugins, errors = load_plugins(tmp_path)
    assert list(plugins) == ["double"]
    assert set(errors) == {"syntax", "raises", "missing", "wrong"}
    assert errors["raises"].startswith("RuntimeError")
    assert "boom at import" in errors["raises"]
    assert errors["syntax"].startswith("SyntaxError")


def test_unknown_plugin_in_pipeline():
    plugins, _ = load_plugins(HERE / "plugins")
    with pytest.raises(KeyError):
        run_pipeline("x", plugins, ["missing"])
