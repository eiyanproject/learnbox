import tracemalloc
import weakref


class ImageCache:
    def __init__(self, loader):
        self.loader = loader
        self.loads = 0
        self._items = weakref.WeakValueDictionary()

    def get(self, key):
        item = self._items.get(key)
        if item is None:
            item = self.loader(key)
            self._items[key] = item
            self.loads += 1
        return item


class Node:
    def __init__(self, name, parent=None):
        self.name = name
        self._parent = None
        self.parent = parent
        self.children = []

    @property
    def parent(self):
        return self._parent() if self._parent is not None else None

    @parent.setter
    def parent(self, node):
        self._parent = weakref.ref(node) if node is not None else None

    def add(self, child):
        child.parent = self
        self.children.append(child)
        return child


def track_cleanup(obj, log, label):
    weakref.finalize(obj, log.append, label)


def peak_allocation(func):
    tracemalloc.start()
    try:
        func()
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return peak
