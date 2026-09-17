---
title: A plugin architecture
summary: Discover and load modules at runtime with importlib, validate them against a Protocol, and isolate failures so one bad plugin cannot break the app.
order: 9
files: [loader.py, plugins/shout.py, plugins/reverse.py]
run: python loader.py
hints:
  - "`discover(folder)`: `sorted(p for p in Path(folder).glob(\"*.py\") if not p.name.startswith(\"_\"))`."
  - "`load_module(path)`: `spec = importlib.util.spec_from_file_location(f\"plugins.{path.stem}\", path)`, `module = importlib.util.module_from_spec(spec)`, `spec.loader.exec_module(module)`, return it."
  - "`load_plugins`: for each path, `try:` load it and `plugin = module.plugin`; if `isinstance(plugin, TextPlugin)`, store it under `plugin.name`; otherwise record an error. `except Exception as e: errors[path.stem] = f\"{type(e).__name__}: {e}\"`."
  - "`run_pipeline(text, plugins, order)`: `for name in order: text = plugins[name].transform(text)`; an unknown name raises `KeyError`."
---

Many programs are extended by dropping a file into a folder: editors, static
site generators, test runners, CI tools. The host program **discovers** the
files, **loads** them as modules, checks they provide what it expects, and
keeps going if one of them is broken.

## Loading a module from a path

`import` needs a module on `sys.path`. To load an arbitrary file, use
`importlib` directly:

```python
import importlib.util
from pathlib import Path

def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(f"plugins.{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)        # runs the file's top-level code
    return module
```

For modules that **are** importable by name (installed packages, a package
directory on `sys.path`), `importlib.import_module("myapp.plugins.csv")` is simpler.

Installed packages advertise plugins through **entry points**
(`importlib.metadata.entry_points(group="myapp.plugins")`), which is how pytest
finds its plugins.

## Defining the contract

Tell plugin authors exactly what to provide. A `Protocol` documents it and lets
you check it at runtime:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class TextPlugin(Protocol):
    name: str
    def transform(self, text: str) -> str: ...
```

Each plugin module exposes a `plugin` object that satisfies it. `isinstance`
with a runtime-checkable protocol checks the attributes and methods exist; it
cannot check signatures, so validate what matters.

## Failure isolation

Loading a plugin runs someone else's code. It can have syntax errors, raise at
import, or provide the wrong thing. None of that should stop the application:

```python
errors = {}
try:
    module = load_module(path)
except Exception as e:           # deliberately broad: this is a boundary
    errors[path.stem] = f"{type(e).__name__}: {e}"
```

Catching broadly is right **at a boundary** like this, as long as the failure
is recorded and reported, not swallowed.

## Security note

Loading a plugin executes arbitrary code with your program's permissions. Only
load plugins from locations you control. There is no sandboxing a Python module
from inside Python.

## Your turn

The workspace has `loader.py` and a `plugins/` folder (the tests add a few
plugins of their own, including broken ones).

- `TextPlugin`: a runtime-checkable `Protocol` with `name: str` and
  `transform(text) -> str`
- `discover(folder)`: sorted `.py` paths in the folder, skipping names starting with `_`
- `load_module(path)`: load one file as a module with `importlib.util`
- `load_plugins(folder)`: returns `(plugins, errors)`: a dict from
  `plugin.name` to the plugin object, and a dict from file stem to an error
  string for files that failed to load, lack a `plugin` attribute, or whose
  `plugin` does not satisfy `TextPlugin`
- `run_pipeline(text, plugins, order)`: apply plugins in the given order
- finish `plugins/shout.py` (name `"shout"`, upper-cases and adds `!`) and
  `plugins/reverse.py` (name `"reverse"`, reverses the text)
