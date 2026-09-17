import pytest

from inventory import Inventory


def test_add():
    inv = Inventory()
    inv.add("apple", 3)
    assert inv.stock("apple") > 0
