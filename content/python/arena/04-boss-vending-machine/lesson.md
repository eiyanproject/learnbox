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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **boss round** | the section's final, longer challenge |
| **cents** | money counted as whole numbers of the smallest unit, so no decimals |
| **credit** | money inserted and not yet spent |
| **change** | the credit minus the price, given back as coins |
| **fewest coins** | take as many of the largest coin as fit, then the next (works for 500, 100, 50, 10) |
| **refund** | the whole credit given back as coins |
| **stock** | each item's price and quantity |
| **sales** | the total of every price paid |
| **own copy** | the machine copies the dict, so later changes to it do not affect the machine |
| **check order** | unknown item, then sold out, then not enough credit; a refusal changes nothing |

### Python names and functions

| Name | What it does |
|---|---|
| `class VendingMachine:` with `__init__` | the class to finish |
| `dict(stock)` | a copy of the stock dict |
| `raise InvalidCoin`, `UnknownItem`, `SoldOut`, `NotEnoughCredit` | the exception classes already written at the top of the file |
| `divmod(amount, coin)` | how many coins fit, and what is left |
| `sorted(names)` | the in-stock names in order |
| `for coin in (500, 100, 50, 10):` | largest coin first |

### Errors

| Error | Means |
|---|---|
| `InvalidCoin` | a coin other than 10, 50, 100 or 500 |
| `UnknownItem` | an item the machine does not have |
| `SoldOut` | none of that item left |
| `NotEnoughCredit` | the credit is less than the price |

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
to `0`, and return the change: the credit minus the price, as coins. A
refused purchase leaves the credit, the stock and `sales` exactly as they
were, so the customer can try again or ask for a refund.

- `sales` is the total of every price paid so far, starting at `0`.

### Change

Change, and a refund, is always a list of coins from largest to smallest,
using as few coins as possible: 660 is `[500, 100, 50, 10]`, and 0 is `[]`.
A refund is worked out from the amount, not from the coins that went in: ten
`10`s inserted come back as `[100]`. With these coin values, taking as many of
the largest coin as fit, then the next, and so on, always gives the fewest
coins.

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
