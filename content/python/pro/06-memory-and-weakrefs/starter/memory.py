import tracemalloc
import weakref


class ImageCache:
    def __init__(self, loader):
        self.loader = loader
        self.loads = 0
        self._items = {}  # a plain dict keeps every image alive forever

    def get(self, key):
        if key not in self._items:
            self._items[key] = self.loader(key)
            self.loads += 1
        return self._items[key]


class Node:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent  # a strong back-reference: every tree is a cycle
        self.children = []

    def add(self, child):
        child.parent = self
        self.children.append(child)
        return child


def track_cleanup(obj, log, label):
    pass


def peak_allocation(func):
    pass
