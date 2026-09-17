import pytest

from functions import apply_all, describe, make_tag, sort_people, total


def test_total():
    assert total() == 0
    assert total(1, 2, 3) == 6
    assert total(1, 2, start=10) == 13


def test_total_unpacking():
    nums = [4, 5, 6]
    assert total(*nums) == 15


def test_describe_plain():
    assert describe("cat") == "cat"


def test_describe_sorted_attributes():
    assert describe("cat", color="grey", age=3) == "cat (age=3, color=grey)"


def test_make_tag():
    assert make_tag("p", "hi") == "<p>hi</p>"
    assert make_tag("p", "hi", cls="note") == '<p class="note">hi</p>'
    assert make_tag("span", "x", id="a", cls="b") == '<span class="b" id="a">x</span>'


def test_make_tag_keyword_only():
    with pytest.raises(TypeError):
        make_tag("p", "hi", "note")


def test_apply_all():
    assert apply_all([str.upper, len, lambda s: s[::-1]], "abc") == ["ABC", 3, "cba"]
    assert apply_all([], 1) == []


def test_sort_people():
    people = [("dewi", 30), ("ana", 41), ("budi", 30), ("citra", 25)]
    assert sort_people(people) == [("ana", 41), ("budi", 30), ("dewi", 30), ("citra", 25)]
    assert people[0] == ("dewi", 30), "do not change the input list"
