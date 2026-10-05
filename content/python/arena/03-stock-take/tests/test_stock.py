from stock import stock_take


def test_the_example():
    lines = [
        "widget, 4, 2.50",
        "# counted on Tuesday",
        "Gadget, 1, 10",
        "widget, two, 2.50",
        " WIDGET ,1,2.50",
    ]
    assert stock_take(lines) == ({"widget": 5, "gadget": 1}, 22.5, [4])


def test_nothing_to_count():
    assert stock_take([]) == ({}, 0.0, [])


def test_comments_and_blanks_are_not_skips_but_are_numbered():
    lines = ["", "   ", "# note", "bolt, 2, 0.25", "nonsense"]
    assert stock_take(lines) == ({"bolt": 2}, 0.5, [5])


def test_wrong_number_of_parts():
    quantities, total, skipped = stock_take(["bolt, 2", "bolt, 2, 1, 9", "nut, 1, 1"])
    assert quantities == {"nut": 1}
    assert skipped == [1, 2]


def test_empty_name():
    assert stock_take([" , 2, 1.00"]) == ({}, 0.0, [1])


def test_bad_quantity():
    lines = ["a, 1.5, 1", "b, -1, 1", "c, , 1", "d, 3, 1"]
    assert stock_take(lines) == ({"d": 3}, 3.0, [1, 2, 3])


def test_bad_price():
    lines = ["a, 1, free", "b, 1, -0.01", "c, 2, 0"]
    assert stock_take(lines) == ({"c": 2}, 0.0, [1, 2])


def test_total_is_rounded():
    assert stock_take(["a, 3, 0.1"])[1] == 0.3
    assert stock_take(["a, 1, 0.1", "b, 1, 0.2"])[1] == 0.3


def test_a_skipped_line_adds_nothing():
    quantities, total, skipped = stock_take(["a, 2, 5", "a, x, 5", "a, 1, 5"])
    assert quantities == {"a": 3}
    assert total == 15.0
    assert skipped == [2]
