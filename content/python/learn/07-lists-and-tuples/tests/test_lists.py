from lists import bounding_box, chunk, rotate, second_largest


def test_second_largest():
    assert second_largest([4, 9, 9, 2]) == 4
    assert second_largest([1, 2]) == 1
    assert second_largest([-5, -1, -3]) == -3


def test_second_largest_none():
    assert second_largest([7, 7, 7]) is None
    assert second_largest([]) is None


def test_second_largest_does_not_change_input():
    data = [3, 1, 2]
    second_largest(data)
    assert data == [3, 1, 2]


def test_chunk():
    assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
    assert chunk([1, 2, 3], 3) == [[1, 2, 3]]
    assert chunk([], 4) == []


def test_rotate():
    assert rotate([1, 2, 3, 4, 5], 2) == [4, 5, 1, 2, 3]
    assert rotate([1, 2, 3], 0) == [1, 2, 3]


def test_rotate_wraps_large_k():
    assert rotate([1, 2, 3], 4) == [3, 1, 2]


def test_rotate_empty_and_unchanged_input():
    assert rotate([], 3) == []
    data = [1, 2, 3]
    rotate(data, 1)
    assert data == [1, 2, 3]


def test_bounding_box():
    assert bounding_box([(1, 5), (-2, 3), (4, -1)]) == ((-2, -1), (4, 5))
    assert bounding_box([(0, 0)]) == ((0, 0), (0, 0))
