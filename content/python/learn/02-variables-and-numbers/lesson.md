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

A **variable** is a name that points at a value, so you can refer to the
value later by its name. You create one with `=`:

```pycon
>>> city = "Jakarta"
>>> population = 10_560_000     # the underscores only make it easier to read
>>> growth = 1.8
>>> is_capital = True
```

Read `=` as "is set to", not "equals". `city = "Jakarta"` is an instruction:
take the value on the right and attach the name on the left to it. (Checking
whether two things are equal is a different operator, `==`, which comes in
the lesson on decisions.) Once a name exists, using it gives you its value:

```pycon
>>> city
'Jakarta'
>>> population * 2
21120000
```

Names may contain letters, digits and underscores, but cannot start with a
digit, and capitals count: `total` and `Total` are two different names. The
Python habit is lower case with underscores between words, as in
`is_capital`. Using a name before you have created it is a `NameError`.

The underscores inside `10_560_000` are only there to make the number easier
for people to read. Python ignores them, so it is the same number as
`10560000`.

In many languages you must declare a variable's type before you use it, for
example "this is a whole number". Python has no such step. It works out the
type from the value itself, and `type()` tells you what it decided:

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

`int` is short for integer and `float` for floating-point number, the
computer's name for a number with a fractional part. `2` and `2.0` are equal
in value but are different types: one is an `int`, the other a `float`.
`str` is short for string, and `bool` for Boolean, after the mathematician
George Boole. `True` and `False` must be written with a capital first letter.

## Arithmetic

```pycon
>>> 7 + 2
9
>>> 7 - 2
5
>>> 7 * 2
14
>>> 7 / 2      # ordinary division always gives a float
3.5
>>> 7 // 2     # floor division: round down to a whole number
3
>>> 7 % 2      # the remainder
1
>>> 7 ** 2     # power
49
```

`/` always gives a `float`, even when the division comes out exact:

```pycon
>>> 6 / 2
3.0
```

`//` and `%` are a pair. `//` answers "how many whole times does it fit?"
and `%` (read "modulo" or "mod") answers "what is left over after that?".
Splitting 130 minutes into hours and minutes:

```pycon
>>> minutes = 130
>>> minutes // 60      # whole hours
2
>>> minutes % 60       # minutes left over
10
```

60 fits into 130 twice, which uses up 120, and 10 is left over: 2 hours and
10 minutes. The same pair turns up whenever you split things into groups of
a fixed size.

"Round down" for `//` means towards the smaller number, which matters once
negative numbers are involved: `-7 // 2` is `-4`, not `-3`, because -4 is
below -3.5.

### Which operation happens first

Python follows the order you learned in maths: `**` first, then `*`, `/`,
`//` and `%`, then `+` and `-`. Operations of the same rank go from left to
right. Brackets override all of this, and adding them when you are unsure
costs nothing:

```pycon
>>> 2 + 3 * 4
14
>>> (2 + 3) * 4
20
>>> 2 * 3 ** 2      # the power first: 2 * 9
18
```

### Floats are close, not exact

A float is stored in binary (base 2), and many simple decimal fractions,
such as 0.1, have no exact binary form, the same way 1/3 has no exact form as
a decimal (0.3333...). Python stores the nearest number it can, and the tiny
difference sometimes shows up in a result:

```pycon
>>> 0.1 + 0.2
0.30000000000000004
>>> round(0.1 + 0.2, 2)
0.3
```

This is not a bug in Python; every language that uses standard floats does
the same. For money and similar values, round the result to the number of
decimal places you need, as this lesson's exercise does.

`round(value, digits)` rounds to that many decimal places, and `round(value)`
with no second argument rounds to a whole number. One surprise: when a number
is exactly halfway, Python rounds to the nearest **even** number, so
`round(2.5)` is `2` and `round(3.5)` is `4`. This is called banker's rounding,
and it stops halves from always pushing totals upwards.

```pycon
>>> round(3.14159, 2)
3.14
>>> round(2.5)
2
>>> round(3.5)
4
```

## Reassigning

A variable can be pointed at a new value at any time, and the name lets go of
the old value. Python always works out the right-hand side first and only then
attaches the name, so a line can use a variable's current value to compute its
next one. In maths `count = count + 1` would be nonsense, but here it means
"take the value of count, add one, and make that the new count":

```pycon
>>> count = 5
>>> count = count + 1
>>> count += 1          # the same thing, shorter
>>> count
7
```

`+=` is shorthand for "add to this variable". There are matching shorthands
for the other operators: `-=`, `*=`, `/=`, `//=` and `%=`.

## Converting between types

A value's type decides what you can do with it. A number typed by a user or
read from a file arrives as text, and text cannot be added to a number until
you convert it. Each type's name works as a function that converts to that
type:

```pycon
>>> int("42")
42
>>> float("2.5")
2.5
>>> str(99)        # the quotes show it is text now
'99'
>>> int(7.9)       # cuts off, does not round
7
```

`int()` on a float throws away everything after the decimal point, so it
moves towards zero: `int(-7.9)` is `-7`. Use `round()` when you want the
nearest whole number instead.

A conversion only works when the text really is a number of that type.
`int("2.5")` is an error, because `2.5` is not a whole number; go through
`float()` first if the text may contain a decimal point:

```pycon
>>> int("2.5")
Traceback (most recent call last):
  ...
ValueError: invalid literal for int() with base 10: '2.5'
>>> int(float("2.5"))
2
```

## Try it interactively

The **Run** button here uses `python -i`. The `-i` stands for interactive:
Python runs the file as usual and then, instead of exiting, leaves you at a
`>>>` prompt where every variable the file created still exists. Type `total`
and press Enter to see its value, or try out a calculation with the other
variables before you write it into the file. Leave with `exit()`.

If you change the file, the prompt does not see the change. Leave it and press
**Run** again to load the new version.

## Your turn

`shopping.py` has prices and quantities. Fill in the variables so that:

- `apples_total` is the cost of the apples (price times count)
- `bread_total` is the cost of the bread
- `total` is the two added together, **rounded to 2 decimal places**
- `change` is `paid - total`, rounded to 2 decimal places
- `boxes` is how many **full** boxes of 6 you can fill with `eggs`
- `loose_eggs` is how many eggs are left over once those boxes are full

Leave the prices and quantities as they are; one of the tests checks that
they have not changed. Compute every answer from those variables, for
example `apple_price * apple_count`, rather than typing in a number you
worked out by hand: a formula keeps working if a price changes, a typed
number does not. Use `//` for `boxes` so that it is a whole number (an
`int`); the tests check its type as well as its value.
