from comprehensions import evens_squared, flatten, lengths, multiplication_table


def test_evens_squared():
    assert evens_squared([1, 2, 3, 4, 5, 6]) == [4, 16, 36]
    assert evens_squared([1, 3]) == []
    assert evens_squared([-2, 0]) == [4, 0]


def test_lengths():
    assert lengths(["ana", "budi", ""]) == {"ana": 3, "budi": 4, "": 0}


def test_flatten():
    assert flatten([[1, 2], [3], [], [4, 5]]) == [1, 2, 3, 4, 5]
    assert flatten([]) == []


def test_multiplication_table_small():
    assert multiplication_table(1) == [[1]]
    assert multiplication_table(2) == [[1, 2], [2, 4]]


def test_multiplication_table_five():
    table = multiplication_table(5)
    assert len(table) == 5
    assert all(len(row) == 5 for row in table)
    assert table[2][3] == 12
    assert table[4] == [5, 10, 15, 20, 25]
