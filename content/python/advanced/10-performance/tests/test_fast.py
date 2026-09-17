import time

from fast import build_report, common_items, has_pair_with_sum, word_frequencies

# Sized so the quadratic versions take seconds and the linear ones milliseconds.
LIMIT = 0.5


def timed(fn, *args):
    start = time.perf_counter()
    result = fn(*args)
    return result, time.perf_counter() - start


def test_common_items_correct():
    assert common_items([3, 1, 3, 2, 5], [5, 3, 9, 3]) == [3, 5]
    assert common_items([], [1]) == []


def test_common_items_fast():
    n = 20_000
    a = list(range(n))
    b = list(range(n // 2, n + n // 2))
    result, secs = timed(common_items, a, b)
    assert result == list(range(n // 2, n))
    assert secs < LIMIT, f"took {secs:.2f}s"


def test_pair_correct():
    assert has_pair_with_sum([1, 4, 6, 9], 10) is True
    assert has_pair_with_sum([5, 1], 10) is False
    assert has_pair_with_sum([5, 5], 10) is True
    assert has_pair_with_sum([5], 10) is False


def test_pair_fast():
    nums = list(range(0, 12_000, 2))
    result, secs = timed(has_pair_with_sum, nums, -1)
    assert result is False
    assert secs < LIMIT, f"took {secs:.2f}s"


def test_word_frequencies_correct():
    assert word_frequencies("b a b c a b") == {"b": 3, "a": 2, "c": 1}
    assert list(word_frequencies("z y z")) == ["z", "y"]


def test_word_frequencies_fast():
    text = " ".join(f"w{i % 10_000}" for i in range(40_000))
    result, secs = timed(word_frequencies, text)
    assert len(result) == 10_000 and result["w0"] == 4
    assert secs < LIMIT, f"took {secs:.2f}s"


def test_build_report_correct():
    assert build_report([("a", 1), ("b", 2.5)]) == "a: 1\nb: 2.5\n"
    assert build_report([]) == ""


def test_build_report_fast():
    rows = [(f"row{i}", "x" * 50) for i in range(100_000)]
    result, secs = timed(build_report, rows)
    assert result.count("\n") == 100_000
    assert secs < LIMIT, f"took {secs:.2f}s"
