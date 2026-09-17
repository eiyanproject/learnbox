import importlib.util
from pathlib import Path
from typing import Protocol, runtime_checkable

HERE = Path(__file__).parent


@runtime_checkable
class TextPlugin(Protocol):
    name: str

    def transform(self, text: str) -> str: ...


def discover(folder):
    return sorted(p for p in Path(folder).glob("*.py") if not p.name.startswith("_"))


def load_module(path):
    path = Path(path)
    spec = importlib.util.spec_from_file_location(f"plugins.{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_plugins(folder):
    plugins, errors = {}, {}
    for path in discover(folder):
        try:
            module = load_module(path)
        except Exception as e:
            errors[path.stem] = f"{type(e).__name__}: {e}"
            continue
        plugin = getattr(module, "plugin", None)
        if plugin is None:
            errors[path.stem] = "no `plugin` attribute"
        elif not isinstance(plugin, TextPlugin):
            errors[path.stem] = "plugin does not satisfy TextPlugin"
        else:
            plugins[plugin.name] = plugin
    return plugins, errors


def run_pipeline(text, plugins, order):
    for name in order:
        text = plugins[name].transform(text)
    return text


if __name__ == "__main__":
    plugins, errors = load_plugins(HERE / "plugins")
    print("loaded:", sorted(plugins))
    print("errors:", errors)
    print(run_pipeline("hello plugins", plugins, ["reverse", "shout"]))
