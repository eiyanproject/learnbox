---
title: "Round 3: Stock take"
summary: Read a messy stock list, total it up, and report what could not be read.
order: 3
files: [stock.py]
run: python -i stock.py
challenge:
  minutes: 20
  xp: 250
  requires:
    xp: 600
    badges: [beginner-1]
---

The warehouse sent its stock list as text, typed by hand, and the auditor is
at the door.

## The task

In `stock.py`, write `stock_take(lines)`.

`lines` is a list of strings. A good line has three parts separated by
commas: an item name, a whole-number quantity and a unit price.

```text
widget, 4, 2.50
```

Return a tuple of three things:

1. **a dict** from item name to the total quantity of that item. Names are
   lower-cased and stripped, and an item that appears on several lines has
   its quantities added together.
2. **the total value** of everything: quantity times price, summed over the
   good lines and rounded to 2 decimals.
3. **a list of the line numbers that were skipped**, counting from 1, in
   order.

Spaces around each part do not matter: `" WIDGET ,1,2.50"` is a good line.

Skip a line, and record its number, when any of these is true:

- it does not have exactly three parts
- the name is empty
- the quantity is not a whole number (`1.5`, `two` or nothing at all), or is
  negative; zero is fine
- the price is not a number, or is negative; zero is fine

Blank lines (including lines of only spaces) and lines starting with `#` are
comments: ignore them without recording them as skipped. They still count
when numbering lines. A skipped line adds nothing to the quantities or the
total.

```text
stock_take([
    "widget, 4, 2.50",
    "# counted on Tuesday",
    "Gadget, 1, 10",
    "widget, two, 2.50",
    " WIDGET ,1,2.50",
])
->  ({"widget": 5, "gadget": 1}, 22.5, [4])
```

Line 1 is 4 widgets at 2.50 (10.00). Line 2 is a comment. Line 3 is one
gadget at 10 (10.00). Line 4 is skipped, because `two` is not a number. Line
5 is one more widget at 2.50 (2.50), and its name is `widget` once stripped
and lower-cased. So there are 5 widgets and 1 gadget, worth 22.50 in all, and
only line 4 was skipped. With no lines at all, the result is
`({}, 0.0, [])`.
