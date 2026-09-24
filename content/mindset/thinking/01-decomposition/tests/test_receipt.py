import pytest

from receipt import format_receipt, line_total, subtotal, tax, total

ITEMS = [("apple", 2, 1.50), ("pear", 1, 2.00)]


def test_line_total():
    assert line_total(2, 1.50) == 3.00
    assert line_total(1, 2.00) == 2.00


def test_line_total_rounds():
    assert line_total(3, 0.335) == 1.01


def test_subtotal_sums_the_lines():
    assert subtotal(ITEMS) == 5.00


def test_subtotal_of_nothing():
    assert subtotal([]) == 0


def test_tax_is_ten_percent_by_default():
    assert tax(5.00) == 0.50


def test_tax_rate_can_be_changed():
    assert tax(100, 0.2) == 20.00


def test_total_includes_tax():
    assert total(ITEMS) == 5.50


def test_receipt_has_a_row_per_item():
    lines = format_receipt(ITEMS).splitlines()
    assert lines[0].startswith("apple")
    assert lines[1].startswith("pear")


def test_receipt_ends_with_the_summary():
    lines = format_receipt(ITEMS).splitlines()
    assert lines[-3] == "SUBTOTAL 5.00"
    assert lines[-2] == "TAX 0.50"
    assert lines[-1] == "TOTAL 5.50"


def test_receipt_of_an_empty_basket_still_has_a_summary():
    lines = format_receipt([]).splitlines()
    assert lines == ["SUBTOTAL 0.00", "TAX 0.00", "TOTAL 0.00"]


def test_the_pieces_are_usable_on_their_own():
    """The point of the decomposition: each part stands alone."""
    assert line_total(4, 2.5) == 10.0
    assert tax(10) == 1.0
