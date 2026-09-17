import pytest

from inventory import Inventory


@pytest.fixture
def stocked():
    inv = Inventory()
    inv.add("pear", 2)
    inv.add("apple", 5)
    inv.add("fig", 2)
    return inv


def test_add_new_and_existing():
    inv = Inventory()
    inv.add("apple", 3)
    inv.add("apple", 4)
    assert inv.stock("apple") == 7


@pytest.mark.parametrize("qty", [0, -1])
def test_add_rejects_non_positive(qty):
    inv = Inventory()
    with pytest.raises(ValueError):
        inv.add("apple", qty)
    assert inv.items() == []


def test_add_minimum_quantity():
    inv = Inventory()
    inv.add("apple", 1)
    assert inv.stock("apple") == 1


def test_stock_unknown_is_zero():
    assert Inventory().stock("ghost") == 0


def test_remove_partial(stocked):
    stocked.remove("apple", 3)
    assert stocked.stock("apple") == 2
    assert "apple" in stocked.items()


def test_remove_one(stocked):
    stocked.remove("apple", 1)
    assert stocked.stock("apple") == 4


def test_remove_exact_forgets_item(stocked):
    stocked.remove("pear", 2)
    assert stocked.stock("pear") == 0
    assert stocked.items() == ["apple", "fig"]


def test_remove_too_many_changes_nothing(stocked):
    with pytest.raises(ValueError, match="not enough"):
        stocked.remove("pear", 3)
    assert stocked.stock("pear") == 2


def test_remove_unknown(stocked):
    with pytest.raises(ValueError):
        stocked.remove("ghost", 1)
    assert "ghost" not in stocked.items()


@pytest.mark.parametrize("qty", [0, -2])
def test_remove_rejects_non_positive(stocked, qty):
    with pytest.raises(ValueError):
        stocked.remove("apple", qty)
    assert stocked.stock("apple") == 5


def test_items_sorted(stocked):
    assert stocked.items() == ["apple", "fig", "pear"]


def test_low_stock_boundary_and_order(stocked):
    stocked.add("kiwi", 1)
    assert stocked.low_stock(2) == ["kiwi", "fig", "pear"]
    assert stocked.low_stock(1) == ["kiwi"]
    assert stocked.low_stock(0) == []
    assert stocked.low_stock(5) == ["kiwi", "fig", "pear", "apple"]


def test_total_units(stocked):
    assert stocked.total_units() == 9
    assert Inventory().total_units() == 0
