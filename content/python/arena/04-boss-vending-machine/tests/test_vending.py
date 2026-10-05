import pytest

from vending import InvalidCoin, NotEnoughCredit, SoldOut, UnknownItem, VendingError, VendingMachine


@pytest.fixture
def machine():
    return VendingMachine({"cola": (150, 2), "gum": (60, 0), "tea": (120, 5)})


def test_starts_empty_handed(machine):
    assert machine.credit == 0
    assert machine.sales == 0


def test_insert_returns_the_running_credit(machine):
    assert machine.insert(100) == 100
    assert machine.insert(50) == 150
    assert machine.credit == 150


@pytest.mark.parametrize("coin", [1, 5, 20, 1000, 0, -10])
def test_bad_coins_are_refused(machine, coin):
    machine.insert(10)
    with pytest.raises(InvalidCoin):
        machine.insert(coin)
    assert machine.credit == 10


def test_buy_with_exact_money(machine):
    machine.insert(100)
    machine.insert(50)
    assert machine.buy("cola") == []
    assert machine.credit == 0
    assert machine.sales == 150
    assert machine.quantity("cola") == 1


def test_buy_gives_change_in_the_fewest_coins(machine):
    machine.insert(500)
    assert machine.buy("tea") == [100, 100, 100, 50, 10, 10, 10]
    machine.insert(500)
    machine.insert(500)
    assert machine.buy("cola") == [500, 100, 100, 100, 50]


def test_sales_add_up(machine):
    for _ in range(2):
        machine.insert(500)
        machine.buy("tea")
    assert machine.sales == 240
    assert machine.quantity("tea") == 3


def test_unknown_item(machine):
    machine.insert(500)
    with pytest.raises(UnknownItem):
        machine.buy("crisps")
    assert machine.credit == 500
    with pytest.raises(UnknownItem):
        machine.quantity("crisps")


def test_sold_out(machine):
    machine.insert(100)
    with pytest.raises(SoldOut):
        machine.buy("gum")
    assert machine.credit == 100
    assert machine.sales == 0


def test_sold_out_is_checked_before_credit(machine):
    with pytest.raises(SoldOut):
        machine.buy("gum")


def test_not_enough_credit(machine):
    machine.insert(100)
    with pytest.raises(NotEnoughCredit):
        machine.buy("cola")
    assert machine.credit == 100
    assert machine.quantity("cola") == 2
    assert machine.sales == 0


def test_selling_the_last_one(machine):
    for _ in range(2):
        machine.insert(100)
        machine.insert(50)
        machine.buy("cola")
    assert machine.quantity("cola") == 0
    machine.insert(500)
    with pytest.raises(SoldOut):
        machine.buy("cola")


def test_refund(machine):
    assert machine.refund() == []
    for coin in [10, 10, 50, 100, 500]:
        machine.insert(coin)
    assert machine.refund() == [500, 100, 50, 10, 10]
    assert machine.credit == 0
    assert machine.sales == 0


def test_refund_uses_the_fewest_coins(machine):
    for _ in range(6):
        machine.insert(100)
    for _ in range(6):
        machine.insert(10)
    assert machine.refund() == [500, 100, 50, 10]


def test_available_is_sorted_and_in_stock_only(machine):
    assert machine.available() == ["cola", "tea"]
    for _ in range(2):
        machine.insert(500)
        machine.buy("cola")
    assert machine.available() == ["tea"]


def test_the_machine_keeps_its_own_stock():
    stock = {"cola": (150, 1)}
    machine = VendingMachine(stock)
    stock["cola"] = (1, 99)
    stock["gum"] = (60, 3)
    assert machine.quantity("cola") == 1
    assert machine.available() == ["cola"]
    machine.insert(100)
    with pytest.raises(NotEnoughCredit):
        machine.buy("cola")


def test_two_machines_do_not_share(machine):
    other = VendingMachine({"cola": (150, 2)})
    machine.insert(500)
    machine.buy("cola")
    assert other.credit == 0
    assert other.sales == 0
    assert other.quantity("cola") == 2


def test_every_refusal_is_a_vending_error():
    for cls in (InvalidCoin, UnknownItem, SoldOut, NotEnoughCredit):
        assert issubclass(cls, VendingError)
