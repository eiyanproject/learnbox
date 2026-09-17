import pytest

from classes import Account


def test_new_account_defaults():
    a = Account("Ana")
    assert a.owner == "Ana"
    assert a.balance == 0
    assert a.history == []


def test_opening_balance():
    assert Account("Ana", 100).balance == 100


def test_accounts_do_not_share_history():
    a, b = Account("A"), Account("B")
    a.deposit(5)
    assert b.history == []


def test_deposit_and_withdraw():
    a = Account("Ana", 10)
    a.deposit(15)
    a.withdraw(20)
    assert a.balance == 5
    assert a.history == [("deposit", 15), ("withdraw", 20)]


def test_withdraw_too_much_changes_nothing():
    a = Account("Ana", 10)
    with pytest.raises(ValueError):
        a.withdraw(11)
    assert a.balance == 10
    assert a.history == []


def test_non_positive_amounts():
    a = Account("Ana", 10)
    for bad in (0, -1):
        with pytest.raises(ValueError):
            a.deposit(bad)
        with pytest.raises(ValueError):
            a.withdraw(bad)


def test_transfer():
    a, b = Account("Ana", 50), Account("Budi", 5)
    a.transfer_to(b, 20)
    assert (a.balance, b.balance) == (30, 25)


def test_failed_transfer_changes_neither():
    a, b = Account("Ana", 10), Account("Budi", 5)
    with pytest.raises(ValueError):
        a.transfer_to(b, 11)
    assert (a.balance, b.balance) == (10, 5)
    assert b.history == []


def test_repr():
    assert repr(Account("Ana", 5)) == "Account('Ana', 5)"


def test_equality():
    assert Account("Ana", 5) == Account("Ana", 5)
    assert Account("Ana", 5) != Account("Ana", 6)
    assert Account("Ana", 5) != "Account('Ana', 5)"
