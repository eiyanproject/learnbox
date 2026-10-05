---
title: "Boss: The vending machine"
summary: A class with stock, coins, change and every way a customer can get it wrong.
order: 4
files: [vending.py]
run: python -i vending.py
challenge:
  boss: true
  minutes: 35
  xp: 500
  requires:
    xp: 1000
    badges: [beginner-1]
---

The machine in the corridor has eaten its last coin. You have thirty-five
minutes to write its replacement. Everything in the Beginner section is in
here somewhere.

## The task

In `vending.py`, finish the `VendingMachine` class. Money is counted in
whole cents, so there are no decimals anywhere. The exception classes are
already written for you at the top of the file.

### Setting up

`VendingMachine(stock)` takes a dict from item name to a `(price, quantity)`
tuple:

```python
machine = VendingMachine({"cola": (150, 2), "gum": (60, 0)})
```

The machine keeps its own copy: changing the dict afterwards must not change
the machine.

### Coins

- `insert(coin)` adds a coin to the customer's credit and returns the credit
  so far. The machine takes only `10`, `50`, `100` and `500`. Anything else
  raises `InvalidCoin` and adds nothing.
- `credit` is the amount inserted and not yet spent, starting at `0`.
- `refund()` returns the credit as a list of coins and sets the credit to
  `0`.

### Buying

`buy(name)` sells one item and returns its change as a list of coins.

Check these in order, and raise without changing anything:

1. the machine has never heard of the item: `UnknownItem`
2. none are left: `SoldOut`
3. the credit is less than the price: `NotEnoughCredit`

Otherwise take one from the stock, add the price to `sales`, set the credit
to `0`, and return the change.

- `sales` is the total of every price paid so far, starting at `0`.

### Change

Change, and a refund, is always a list of coins from largest to smallest,
using as few coins as possible: 660 is `[500, 100, 50, 10]`, and 0 is `[]`.

### Looking inside

- `available()` returns a sorted list of the names that are in stock.
- `quantity(name)` returns how many of an item are left, raising
  `UnknownItem` for a name the machine does not have.

```python
machine = VendingMachine({"cola": (150, 2), "gum": (60, 0)})
machine.insert(100)        # 100
machine.insert(100)        # 200
machine.buy("cola")        # [50]
machine.credit             # 0
machine.sales              # 150
machine.quantity("cola")   # 1
machine.available()        # ["cola"]
machine.buy("gum")         # raises SoldOut
```
