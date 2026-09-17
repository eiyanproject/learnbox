import importlib.util
from pathlib import Path
from typing import Protocol, runtime_checkable

HERE = Path(__file__).parent


class TextPlugin:
    pass


def discover(folder):
    pass


def load_module(path):
    pass


def load_plugins(folder):
    pass


def run_pipeline(text, plugins, order):
    pass


if __name__ == "__main__":
    plugins, errors = load_plugins(HERE / "plugins")
    print("loaded:", sorted(plugins))
    print("errors:", errors)
    print(run_pipeline("hello plugins", plugins, ["reverse", "shout"]))
