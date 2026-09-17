import inspect
import itertools

from generators import chunked, countdown, fibonacci, read_records, take


def test_countdown_is_a_generator():
    assert inspect.isgeneratorfunction(countdown)
    assert list(countdown(3)) == [3, 2, 1]
    assert list(countdown(0)) == []


def test_read_records():
    lines = ["# header\n", "ana,31\n", "\n", "  budi,27  \n", "#skip"]
    assert list(read_records(lines)) == [["ana", "31"], ["budi", "27"]]


def test_read_records_is_lazy():
    def exploding():
        yield "a,b"
        raise AssertionError("read past what was needed")

    records = read_records(exploding())
    assert next(records) == ["a", "b"]


def test_fibonacci_infinite():
    assert inspect.isgeneratorfunction(fibonacci)
    assert list(itertools.islice(fibonacci(), 10)) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_take():
    assert take(3, fibonacci()) == [0, 1, 1]
    assert take(5, [1, 2]) == [1, 2]
    assert take(0, fibonacci()) == []


def test_chunked():
    assert list(chunked(range(7), 3)) == [[0, 1, 2], [3, 4, 5], [6]]
    assert list(chunked([], 2)) == []


def test_chunked_works_on_infinite_input():
    first = next(chunked(itertools.count(), 4))
    assert first == [0, 1, 2, 3]
