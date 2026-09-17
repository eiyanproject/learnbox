import gc
import weakref

from memory import ImageCache, Node, peak_allocation, track_cleanup


class Image:
    def __init__(self, key):
        self.key = key


def test_cache_returns_same_live_object():
    cache = ImageCache(Image)
    a = cache.get("logo")
    b = cache.get("logo")
    assert a is b
    assert cache.loads == 1


def test_cache_does_not_keep_objects_alive():
    cache = ImageCache(Image)
    img = cache.get("banner")
    probe = weakref.ref(img)
    del img
    gc.collect()
    assert probe() is None, "the cache kept the image alive"
    cache.get("banner")
    assert cache.loads == 2


def test_node_parent_links():
    root = Node("root")
    child = root.add(Node("child"))
    assert child.parent is root
    assert root.children == [child]
    assert root.parent is None


def test_node_parent_constructor_argument():
    root = Node("root")
    leaf = Node("leaf", parent=root)
    assert leaf.parent is root


def test_tree_is_freed_without_cycle_collector():
    gc.disable()
    try:
        root = Node("root")
        child = root.add(Node("child"))
        root_ref = weakref.ref(root)
        del root
        assert root_ref() is None, "root survived: the child holds a strong reference to its parent"
        assert child.parent is None
    finally:
        gc.enable()


def test_track_cleanup():
    log = []
    img = Image("x")
    track_cleanup(img, log, "image x gone")
    assert log == []
    del img
    gc.collect()
    assert log == ["image x gone"]


def test_peak_allocation():
    small = peak_allocation(lambda: [0] * 10)
    big = peak_allocation(lambda: [str(i) for i in range(200_000)])
    assert big > 5_000_000
    assert small < big / 100
