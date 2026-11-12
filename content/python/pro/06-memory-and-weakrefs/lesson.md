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

Python frees memory for you, so most of the time you never think about it.
But "most of the time" is not always. A long-running server whose memory
creeps up day after day, a cache that quietly holds on to every object it
ever saw, a tree whose nodes are never freed: these are real bugs, and
fixing them needs a picture of when Python actually frees an object. This
lesson gives that picture, and the tools, weak references and
`tracemalloc`, for holding on to objects without keeping them alive, and for
measuring what your code allocates.

## How CPython frees memory

Every object has a **reference count**: how many names, containers and
attributes point at it. `x = []` makes one reference; `y = x` makes a
second; putting it in a list makes a third. Each time a reference goes away
(a name is reassigned or deleted, a function returns and its local variables
vanish, a container drops the item), the count goes down. When it drops to
zero, nothing can reach the object any more, and it is freed immediately -
CPython does not wait for a collector to come round.

```pycon
>>> import sys
>>> x = []
>>> sys.getrefcount(x)       # `x` plus the temporary argument
2
>>> y = x                    # a second name for the same list
>>> sys.getrefcount(x)
3
>>> del y
>>> sys.getrefcount(x)
2
```

`sys.getrefcount` always reports one more than you might expect, because
passing the object to the function creates a temporary reference of its own.

That immediacy is a property of **CPython**, not of Python. PyPy and other
implementations free objects whenever they get to it, so a file whose last
reference has gone may stay open, with its writes not yet saved. Never let a
resource's lifetime rest on refcounting: use `with`, and let the reference
count be an optimisation you benefit from rather than a guarantee you depend
on.

## Cycles

Reference counting cannot free objects that point at each other:

```python
a = {}; b = {"a": a}; a["b"] = b
del a, b                 # counts never reach zero
```

`a` contains `b` and `b` contains `a`. After `del a, b`, nothing in your
program can reach either dict, but each still has a reference from the
other, so neither count reaches zero. This is a **reference cycle**.

The **cycle collector** (the `gc` module) finds such unreachable groups
periodically and frees them. It works, but it is delayed (it runs every so
often, not immediately) and it costs time, because it has to examine the
objects to find the cycles. `gc.collect()` runs it straight away, which is
useful in tests:

```pycon
>>> import gc
>>> a = {}; b = {"a": a}; a["b"] = b
>>> del a, b
>>> gc.collect() >= 2        # it found and freed the two dicts (and maybe more)
True
```

Avoid needless cycles, especially parent-child links in trees (a parent
lists its children, and each child points back at its parent) and caches.
This lesson's `Node` exercise shows how.

You may meet older advice that a cycle containing an object with `__del__`
can never be collected at all. That was true until **Python 3.4**: such
groups were given up on and parked in `gc.garbage`. PEP 442 changed it, and
they are collected now. Cycles are still worth avoiding for the delay and the
cost, but `__del__` no longer makes one permanent.

## Weak references

A **weak reference** points at an object without keeping it alive: it does
not count towards the reference count. You create one with `weakref.ref(obj)`,
and get the object back by *calling* the reference, `r()`. If the object has
been freed in the meantime, calling it returns `None` instead:

```python
import weakref

class Big: ...

obj = Big()
r = weakref.ref(obj)
print(r() is obj)    # the weak reference reaches the object
del obj
print(r())           # None: it was collected
```

```output
True
None
```

`del obj` removed the only strong reference, so the count reached zero and
the object was freed, even though `r` still existed. A weak reference is
how you say "I would like to use this object if it is still around, but I am
not the reason it should stay around."

Run this as a script. At the `>>>` prompt the result is different, because the
prompt keeps the last value it displayed in the variable `_` - a strong
reference that keeps the object alive.

The standard use cases:

- **Back-references**: a child refers to its parent weakly, so the tree has no
  strong cycle. The parent's list of children is what keeps the tree alive;
  the child's link back up is only for finding its way.
- **Caches**: `weakref.WeakValueDictionary` is a dict whose values are held
  weakly. An entry disappears automatically once nothing else uses its value,
  so a cache cannot keep the whole world alive: it hands out objects while
  someone is using them, and forgets them afterwards.
- **Registries of listeners** with `WeakSet`, a set that holds its items
  weakly, so an object that forgets to unsubscribe is still freed, rather
  than being kept alive forever by the registry.

```pycon
>>> import weakref
>>> class Image:
...     def __init__(self, name):
...         self.name = name
...
>>> cache = weakref.WeakValueDictionary()
>>> img = Image("logo")
>>> cache["logo"] = img
>>> "logo" in cache          # alive: img still refers to it
True
>>> del img                  # the last strong reference goes...
>>> "logo" in cache          # ...and so does the cache entry
False
```

Not everything is weak-referenceable: `int`, `str`, `tuple`, `list` and `dict`
instances are not; your own classes are (unless they use `__slots__` without
including `"__weakref__"` in the slots).

## Finalizers

Sometimes something must happen when an object is freed: delete a temporary
directory, close a connection, release a lock. `__del__` is a method Python
calls right before freeing an object, but it runs at unpredictable times, may
run during interpreter shutdown when modules are half torn down, and can
accidentally bring the object back to life. `weakref.finalize` is the robust
way to run cleanup when an object is collected:

```python
weakref.finalize(obj, shutil.rmtree, temp_dir)
```

This registers "when `obj` is collected, call `shutil.rmtree(temp_dir)`".
The finalizer itself only holds a weak reference to `obj`. It runs exactly
once: when `obj` is freed, or at interpreter exit if that comes first.

```pycon
>>> log = []
>>> class Job: ...
...
>>> job = Job()
>>> _ = weakref.finalize(job, log.append, "job cleaned up")
>>> log
[]
>>> del job
>>> log
['job cleaned up']
```

(`_ =` keeps the prompt from displaying the finalizer object, which would
otherwise sit in `_` harmlessly but confusingly.)

The callback and its arguments must not refer to `obj` itself, or it would
keep `obj` alive forever: the finalizer holds its callback strongly, so a
callback that mentions `obj` (for example a lambda that uses it, or a bound
method of it) is a strong reference, and the object can never be freed.

## Measuring

Before fixing a memory problem, measure it. `tracemalloc` records every
memory allocation Python makes while it is running:

```python
import tracemalloc

tracemalloc.start()
data = [str(i) for i in range(100_000)]
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
```

`get_traced_memory()` returns two numbers of bytes: `current`, what is
allocated now, and `peak`, the most that was allocated at any one moment
since `start()`. The peak is usually what matters: a function that briefly
builds a huge temporary list needs that much memory, even if it frees it
before returning.

```pycon
>>> import tracemalloc
>>> tracemalloc.start()
>>> data = [str(i) for i in range(100_000)]
>>> current, peak = tracemalloc.get_traced_memory()
>>> tracemalloc.stop()
>>> peak > 5_000_000         # a hundred thousand small strings: several MB
True
```

Two more tools:

- `sys.getsizeof(obj)` gives one object's own size in bytes, not what it
  references: for a list, that is the list's own array of pointers, not the
  items. A list of a million long strings and a list of a million small
  integers report the same size.
- `tracemalloc.take_snapshot().statistics("lineno")` shows which lines of your
  code allocated the most, sorted biggest first. That points straight at the
  line to look at.

## Your turn

In `memory.py`:

- `ImageCache(loader)`: `get(key)` returns the cached object for `key` if one
  is still alive somewhere, and otherwise calls `loader(key)`, stores the
  result and returns it. It must not keep images alive by itself: once the
  caller drops every reference to an image, the cache entry must go too.
  `loads` counts how many times the loader was called.
- `Node(name, parent=None)`: `children` is a list; `add(child)` appends the
  child, sets its parent to this node, and returns the child. `parent` is a
  property backed by a weak reference (setting it stores a weak reference;
  reading it gives the parent, or `None`), so a tree does not form strong
  cycles. A test switches the cycle collector off and checks that deleting the
  root frees it, after which the child's `parent` is `None`. Passing
  `parent=` to the constructor sets the parent too.
- `track_cleanup(obj, log, label)`: arrange for `label` to be appended to the
  list `log` when `obj` is collected, without keeping `obj` alive.
- `peak_allocation(func)`: the peak bytes allocated while `func()` runs, via
  `tracemalloc`.
