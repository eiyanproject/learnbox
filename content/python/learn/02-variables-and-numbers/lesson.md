---
title: Variables and numbers
summary: Names for values, the four basic types, and arithmetic that does what you expect.
order: 2
files: [shopping.py]
run: python -i shopping.py
hints:
  - "A total is price times quantity: `apples_total = apple_price * apple_count`."
  - "`//` divides and rounds down to a whole number; `%` gives what is left over."
  - "`round(value, 2)` rounds to two decimal places."
---

A **variable** is a name that points at a value. You create one with `=`:

```python
city = "Jakarta"
population = 10_560_000     # underscores are just for readability
growth = 1.8
is_capital = True
```

There is no type declaration. Python works out the type from the value, and
`type()` tells you what it decided:

```pycon
>>> type(population)
<class 'int'>
>>> type(growth)
<class 'float'>
```

## The basic types

| Type    | Example           | What it is |
|---------|-------------------|------------|
| `int`   | `42`, `-7`, `0`   | whole numbers, any size |
| `float` | `3.14`, `2.0`     | numbers with a decimal point |
| `str`   | `"hello"`         | text |
| `bool`  | `True`, `False`   | yes or no |

## Arithmetic

```python
7 + 2    # 9
7 - 2    # 5
7 * 2    # 14
7 / 2    # 3.5   ordinary division always gives a float
7 // 2   # 3     floor division: round down to a whole number
7 % 2    # 1     remainder
7 ** 2   # 49    power
```

`//` and `%` are a pair. Splitting 130 minutes into hours and minutes:

```python
minutes = 130
hours = minutes // 60      # 2
leftover = minutes % 60    # 10
```

Floats are stored in binary, so some decimals come out slightly off:

```pycon
>>> 0.1 + 0.2
0.30000000000000004
>>> round(0.1 + 0.2, 2)
0.3
```

## Reassigning

A variable can be pointed at a new value. The right-hand side is worked out
first, so this adds one:

```python
count = 5
count = count + 1
count += 1          # the same thing, shorter
```

## Converting between types

```python
int("42")      # 42
float("2.5")   # 2.5
str(99)        # "99"
int(7.9)       # 7   (cuts off, does not round)
```

## Try it interactively

The **Run** button here uses `python -i`, which runs the file and then leaves
you at a `>>>` prompt with all its variables defined. Type `total` and press
Enter to look at a value. Leave with `exit()`.

## Your turn

`shopping.py` has prices and quantities. Fill in the variables so that:

- `apples_total` is the cost of the apples (price times count)
- `bread_total` is the cost of the bread
- `total` is the two added together, **rounded to 2 decimal places**
- `change` is `paid - total`, rounded to 2 decimal places
- `boxes` is how many **full** boxes of 6 you can fill with `eggs`
- `loose_eggs` is how many eggs are left over

Leave the prices and quantities as they are.
