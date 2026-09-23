import pytest

from basics import arithmetic_facts, build_matrix, replace_slice, slice_word


def test_true_division_is_always_a_float():
    assert arithmetic_facts(6, 3)["quotient"] == 2.0
    assert isinstance(arithmetic_facts(6, 3)["quotient"], float)


@pytest.mark.parametrize(
    "a, b, floor, remainder",
    [(7, 2, 3, 1), (-7, 2, -4, 1), (7, -2, -4, -1), (10, 5, 2, 0)],
)
def test_floor_and_remainder_follow_the_divisor(a, b, floor, remainder):
    facts = arithmetic_facts(a, b)
    assert facts["floor"] == floor
    assert facts["remainder"] == remainder


def test_the_division_identity_holds():
    for a, b in [(7, 2), (-7, 2), (7, -2), (-7, -2)]:
        f = arithmetic_facts(a, b)
        assert a == f["floor"] * b + f["remainder"]


def test_power():
    assert arithmetic_facts(2, 10)["power"] == 1024


def test_slice_word():
    assert slice_word("Python") == ("Pyt", "hon", "nohtyP", "Pto")


def test_slices_do_not_raise_on_short_words():
    first, last, reversed_, every_other = slice_word("hi")
    assert first == "hi"
    assert last == "hi"
    assert reversed_ == "ih"
    assert every_other == "h"


def test_replace_slice_shortens_the_list():
    assert replace_slice([1, 2, 3, 4, 5]) == [1, 0, 0, 5]


def test_replace_slice_mutates_in_place():
    values = [1, 2, 3, 4, 5]
    assert replace_slice(values) is values


def test_build_matrix_shape_and_contents():
    assert build_matrix(2, 3) == [[0, 1, 2], [3, 4, 5]]
    assert build_matrix(3, 2) == [[0, 1], [2, 3], [4, 5]]


def test_build_matrix_rows_are_independent():
    matrix = build_matrix(2, 2)
    matrix[0][0] = 99
    assert matrix[1][0] == 2
