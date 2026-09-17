---
title: Memory and weak references
summary: Reference counting and the cycle collector, weakref caches that do not keep objects alive, finalizers, and measuring with tracemalloc.
order: 6
files: [memory.py]
run: python -i memory.py
hints:
  - "`ImageCache` keeps a `weakref.WeakValueDictionary`; `get(key)` returns `self._items.get(key)` and otherwise loads, stores and returns the new object. Count `self.loads`."
  - "`Node` holds `self._parent = weakref.ref(parent) if parent else None`; the `parent` property calls the reference: `self._parent() if self._parent else None`."
  - "`track_cleanup(obj, log, label)`: `weakref.finalize(obj, log.append, label)` runs once when `obj` is collected, and must not capture `obj` itself."
  - "`peak_allocation(func)`: `tracemalloc.start()`, call `func()`, `_, peak = tracemalloc.get_traced_memory()`, `tracemalloc.stop()`, return `peak`."
---

## How CPython frees memory

Every object has a **reference count**: how many names, containers and
attributes point at it. When it drops to zero, the object is freed
immediately. This is why `with` is not needed to close a file in simple
scripts: the file is closed the moment the last reference disappears.

```python
import sys
x = []
sys.getrefcount(x)       # 2: `x` plus the temporary argument
```

## Cycles

Reference counting cannot free objects that point at each other:

```python
a = {}; b = {"a": a}; a["b"] = b
del a, b                 # counts never reach zero
```

The **cycle collector** (`gc` module) finds such unreachable groups
periodically. It works, but it is delayed and costs time. Avoid needless
cycles, especially parent-child links in trees and caches, and objects with
`__del__` inside cycles.

## Weak references

A **weak reference** points at an object without keeping it alive:

```python
import weakref

class Big: ...

obj = Big()
r = weakref.ref(obj)
r()          # the object
del obj
r()          # None: it was collected
```

The standard use cases:

- **Back-references**: a child refers to its parent weakly, so the tree has no
  strong cycle.
- **Caches**: `weakref.WeakValueDictionary` drops entries automatically once
  nothing else uses the value, so a cache cannot keep the whole world alive.
- **Registries of listeners** with `WeakSet`, so forgetting to unsubscribe is
  not a leak.

Not everything is weak-referenceable: `int`, `str`, `tuple`, `list` and `dict`
instances are not; your own classes are (unless they use `__slots__` without
`__weakref__`).

## Finalizers

`__del__` runs at unpredictable times and has sharp edges. `weakref.finalize`
is the robust way to run cleanup when an object is collected:

```python
weakref.finalize(obj, shutil.rmtree, temp_dir)
```

The callback must not refer to `obj` itself, or it would keep `obj` alive forever.

## Measuring

```python
import tracemalloc

tracemalloc.start()
data = [str(i) for i in range(100_000)]
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
```

`sys.getsizeof(obj)` gives one object's own size, not what it references.
`tracemalloc.take_snapshot().statistics("lineno")` shows which lines allocated the most.

## Your turn

In `memory.py`:

- `ImageCache(loader)`: `get(key)` returns a cached object if one is still alive,
  otherwise calls `loader(key)`; must not keep images alive by itself. `loads`
  counts loader calls.
- `Node(name, parent=None)`: `children` is a list; adding a child with
  `add(child)` sets its parent. `parent` is a property backed by a weak reference,
  so a tree does not form strong cycles.
- `track_cleanup(obj, log, label)`: append `label` to `log` when `obj` is collected
- `peak_allocation(func)`: the peak bytes allocated while `func()` runs, via `tracemalloc`
