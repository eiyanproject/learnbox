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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **plugin** | a file that extends a program without editing it |
| **plugin architecture** | the host discovers plugin files, loads them while it runs, checks them, and survives broken ones |
| **host** | the program that loads the plugins |
| **discover** | find the plugin files, here a directory listing |
| **glob pattern** | a file-name pattern such as `*.py` |
| **private file** | one whose name starts with `_`, skipped by convention |
| **stem** | a file name without its extension |
| **module spec** | a description of a module to load: its name and where its code is |
| **runtime loading** | loading a file chosen while the program runs, not written into an `import` |
| **entry point** | a package's declaration "I provide a plugin for this app", listed by the host |
| **contract** | what each plugin must provide: an object `plugin` with `name` and `transform` |
| **Protocol** | an interface checked by shape, not inheritance (structural typing) |
| **failure isolation** | one broken plugin means one missing feature, not a crashed program |
| **boundary** | where your code meets code you do not control; the right place for a broad `except` |
| **sandboxing** | restricting what code can do; impossible for a Python module inside Python |
| **pipeline** | applying plugins one after another, each to the result of the one before |

### Python names and functions

| Name | What it does |
|---|---|
| `Path(folder).glob("*.py")` | every `.py` file in the folder |
| `p.name.startswith("_")`, `p.stem` | the private-file check; the name without `.py` |
| `tempfile.mkdtemp()` | an empty scratch folder |
| `importlib.util.spec_from_file_location(name, path)` | a module spec for that file |
| `importlib.util.module_from_spec(spec)` | a new, empty module |
| `spec.loader.exec_module(module)` | runs the file's code inside the module |
| `importlib.import_module("pkg.mod")` | `import` with the name as a string |
| `importlib.metadata.entry_points(group=...)` | the plugins installed packages advertise |
| `@runtime_checkable class TextPlugin(Protocol):` | the contract, checkable with `isinstance` (attributes exist; signatures are not checked) |
| `getattr(module, "plugin")`, `hasattr` | reads or checks the module's `plugin` |
| `except Exception as e:` | catches any ordinary error at the boundary (Ctrl+C still gets through) |
| `f"{type(e).__name__}: {e}"` | an error string such as `RuntimeError: boom at import` |
| `text[::-1]`, `text.upper()` | reversed text; upper case |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python loader.py` | loads the plugins and runs the pipeline |

### Errors

| Error | Means |
|---|---|
| `SyntaxError` | a plugin file that is not valid Python |
| `RuntimeError` | an example of a plugin raising at import |
| `KeyError` | an unknown plugin name in the pipeline order |
| `AttributeError` | a module with no `plugin` attribute |

---

Many programs are extended by dropping a file into a folder: editors,
static site generators, test runners, CI tools. Nobody edits the program
itself; it notices the new file and picks up what it offers. This is a
**plugin architecture**. The host program **discovers** the files, **loads**
them as modules while it runs, checks they provide what it expects, and keeps
going if one of them is broken.

Each of those steps uses something from earlier in the course: paths from
the Files lesson, modules from Modules and packages, protocols from Type
hints, and exception handling at a boundary. This lesson puts them together.

## Discovering plugins

Discovery is a directory listing. `Path.glob("*.py")` finds every file in a
folder matching a pattern, here every `.py` file. Files whose names start
with `_`, such as `__init__.py` or `_helpers.py`, are conventionally private
and skipped. Sorting the result makes the load order the same on every
machine, since the operating system lists files in no guaranteed order:

```pycon
>>> from pathlib import Path
>>> import tempfile
>>> folder = Path(tempfile.mkdtemp())            # an empty scratch folder
>>> for name in ["b.py", "a.py", "_private.py", "notes.txt"]:
...     _ = (folder / name).write_text("")
...
>>> sorted(p.name for p in folder.glob("*.py") if not p.name.startswith("_"))
['a.py', 'b.py']
```

## Loading a module from a path

`import name` only finds modules in the folders on `sys.path` (the Modules
lesson), and the name must be known when you write the code. To load an
arbitrary file, chosen while the program runs, use `importlib` directly:

```python
import importlib.util
from pathlib import Path

def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(f"plugins.{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)        # runs the file's top-level code
    return module
```

The three steps are what `import` does internally, done by hand:

1. `spec_from_file_location(name, path)` creates a **module spec**: a
   description of the module to load, with the name it will have and where
   its code is. The name here is `plugins.` plus the file's stem (its name
   without `.py`).
2. `module_from_spec(spec)` creates a new, empty module object.
3. `spec.loader.exec_module(module)` runs the file's code inside that module,
   top to bottom, the way an import would. Whatever the file defines becomes
   an attribute of the module.

```pycon
>>> _ = (folder / "answer.py").write_text("VALUE = 6 * 7\n")
>>> import importlib.util
>>> spec = importlib.util.spec_from_file_location("plugins.answer", folder / "answer.py")
>>> module = importlib.util.module_from_spec(spec)
>>> spec.loader.exec_module(module)
>>> module.VALUE
42
```

Because the file is run, every error in it surfaces at step 3: a syntax
error, or an exception raised by its top-level code.

For modules that **are** importable by name (installed packages, a package
directory on `sys.path`), `importlib.import_module("myapp.plugins.csv")` is
simpler: it is `import` with the name given as a string.

Installed packages advertise plugins through **entry points**: a package
declares in its `pyproject.toml` "I provide a plugin for `myapp`", and the
host lists them with `importlib.metadata.entry_points(group="myapp.plugins")`.
That is how pytest finds its plugins, without any of them living in one
shared folder.

## Defining the contract

Tell plugin authors exactly what to provide. A `Protocol` documents it and
lets you check it at runtime:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class TextPlugin(Protocol):
    name: str
    def transform(self, text: str) -> str: ...
```

The contract in words: each plugin module exposes an object called `plugin`,
which has a `name` attribute (a string) and a `transform` method that takes
text and returns text. Plugins do not need to import or inherit anything from
the host; matching the shape is enough (structural typing, from the Type
hints lesson).

`isinstance(obj, TextPlugin)` with a runtime-checkable protocol checks that
the attributes and methods **exist**. It cannot check signatures or types,
so a `transform` that takes the wrong arguments still passes; validate what
matters to you separately:

```pycon
>>> from typing import Protocol, runtime_checkable
>>> @runtime_checkable
... class TextPlugin(Protocol):
...     name: str
...     def transform(self, text: str) -> str: ...
...
>>> class Upper:
...     name = "upper"
...     def transform(self, text):
...         return text.upper()
...
>>> isinstance(Upper(), TextPlugin)
True
>>> isinstance("not a plugin", TextPlugin)      # a str has no transform
False
```

## Failure isolation

Loading a plugin runs someone else's code. It can have syntax errors, raise
at import, or provide the wrong thing. None of that should stop the
application: one broken plugin should mean one missing feature and a clear
message, not a program that refuses to start.

```python
errors = {}
try:
    module = load_module(path)
except Exception as e:           # deliberately broad: this is a boundary
    errors[path.stem] = f"{type(e).__name__}: {e}"
```

Elsewhere in this course the advice has been to catch the specific exception
you expect. Here you cannot know what to expect: a plugin can fail in any
way at all. Catching broadly is right **at a boundary** like this, where your
code meets code you do not control, as long as the failure is recorded and
reported, not swallowed. `except Exception` still lets Ctrl+C through, which
derives from `BaseException`. Recording `type(e).__name__` along with the
message gives errors like `RuntimeError: boom at import`, which tell the
plugin's author both what kind of failure it was and why.

```pycon
>>> _ = (folder / "raises.py").write_text("raise RuntimeError('boom at import')\n")
>>> spec = importlib.util.spec_from_file_location("plugins.raises", folder / "raises.py")
>>> try:
...     spec.loader.exec_module(importlib.util.module_from_spec(spec))
... except Exception as e:
...     print(f"{type(e).__name__}: {e}")
...
RuntimeError: boom at import
```

## Security note

Loading a plugin executes arbitrary code with your program's permissions: it
can read and delete your files, open network connections, anything your
program could do. Only load plugins from locations you control. There is no
sandboxing a Python module from inside Python; if untrusted code must run,
it needs a separate, restricted process or machine.

## Your turn

The workspace has `loader.py` and a `plugins/` folder. The tests add
folders of their own, with plugins that work and plugins broken in each of
the ways above.

- `TextPlugin`: a runtime-checkable `Protocol` with `name: str` and
  `transform(text) -> str`.
- `discover(folder)`: the sorted `.py` paths in the folder, skipping names
  that start with `_` (and any file that is not `.py`).
- `load_module(path)`: load one file as a module with `importlib.util`, and
  return the module.
- `load_plugins(folder)`: returns two dicts, `(plugins, errors)`. `plugins`
  maps each `plugin.name` to the plugin object. `errors` maps a file's stem
  to an error string for every file that failed to load, has no `plugin`
  attribute, or whose `plugin` does not satisfy `TextPlugin`. For a file that
  raised, the string starts with the exception's class name and contains its
  message, such as `"RuntimeError: boom at import"`; a syntax error gives a
  string starting with `SyntaxError`. A broken file must not stop the others
  from loading.
- `run_pipeline(text, plugins, order)`: apply the plugins named in `order`,
  one after another, each to the result of the one before, and return the
  final text. An empty `order` returns the text unchanged; an unknown name
  raises `KeyError`.
- finish `plugins/shout.py` (name `"shout"`: upper-cases the text and adds
  `!`) and `plugins/reverse.py` (name `"reverse"`: reverses the text). So
  `"hello"` through `["reverse", "shout"]` gives `"OLLEH!"`.
