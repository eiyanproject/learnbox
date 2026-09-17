import math
import pathlib
import time

from algorithms import binary_search, count_paths, flatten, permutations


def test_flatten():
    assert flatten([1, [2, [3, []]], 4]) == [1, 2, 3, 4]
    assert flatten([]) == []
    assert flatten([[[["deep"]]]]) == ["deep"]


def test_binary_search_found():
    items = list(range(0, 100, 3))
    for i, v in enumerate(items):
        assert binary_search(items, v) == i


def test_binary_search_missing():
    assert binary_search([1, 3, 5], 4) == -1
    assert binary_search([], 1) == -1
    assert binary_search([1, 3, 5], 99) == -1


def test_binary_search_is_logarithmic():
    items = list(range(2_000_000))
    start = time.perf_counter()
    for target in range(0, 2_000_000, 20_000):
        assert binary_search(items, target) == target
    assert time.perf_counter() - start < 0.5, "looks like a linear scan"


def test_binary_search_is_handwritten():
    source = (pathlib.Path(__file__).parent / "algorithms.py").read_text()
    assert "bisect" not in source and ".index(" not in source


def test_permutations():
    assert permutations([]) == [[]]
    assert permutations([1]) == [[1]]
    assert permutations([1, 2, 3]) == [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]


def test_permutations_count():
    assert len(permutations(list("abcdef"))) == math.factorial(6)


def test_count_paths_small():
    assert count_paths(1, 1) == 1
    assert count_paths(2, 2) == 2
    assert count_paths(3, 3) == 6
    assert count_paths(3, 7) == 28


def test_count_paths_fast():
    start = time.perf_counter()
    assert count_paths(30, 30) == math.comb(58, 29)
    assert time.perf_counter() - start < 1, "cache the subproblems"
