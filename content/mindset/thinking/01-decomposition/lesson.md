---
title: Decomposing a problem
summary: Turning one problem you cannot solve into several you can, and why the seams you choose decide how hard the rest will be.
order: 1
files: [receipt.py]
run: python -i receipt.py
hints:
  - "Write the four small functions first and `format_receipt` last - it should read as a summary of the others, not contain their logic."
  - "`line_total` is quantity times price, rounded to 2 decimals. Round once, here, not in three different places."
  - "`subtotal` sums line totals; `tax` is 10% of the subtotal rounded to 2; `total` is subtotal plus tax."
  - "`format_receipt` joins one line per item plus SUBTOTAL, TAX and TOTAL rows - use the functions above rather than recomputing."
---

A problem you cannot hold in your head is not a hard problem; it is several
problems wearing one name. The skill is finding the seams.

## Work from the output backwards

"Print a receipt" is not something you can start typing. But the output has
parts:

```
apple      2 x 1.50 =   3.00
pear       1 x 2.00 =   2.00
SUBTOTAL                5.00
TAX                     0.50
TOTAL                   5.50
```

Each row is a thing to compute, and each computation has a name. The naming is
the decomposition — once every part has a name, you have the function list.

## Good seams have three properties

- **A name you can say without "and".** `calculate_totals_and_format` is two
  functions wearing a trench coat. If the honest name needs "and", split it.
- **Testable alone.** If checking a piece requires standing up half the
  program, it is not a seam, it is a slice through the middle of one.
- **One reason to change.** Tax rules and layout change for entirely different
  reasons and at different times. A function that knows both gets edited twice
  as often, by people thinking about different things.

## Build the boring pieces first

Write `line_total` before `format_receipt`. The small functions have obvious
answers you can check immediately; the assembly is then nearly trivial, because
all the thinking already happened.

Working the other way — starting with the big function and extracting later —
means holding the entire problem in your head at once, which is the thing you
were trying to avoid.

## Where to put the rounding

Rounding in three places gives three chances to disagree. Round **once**, at
the point where a number becomes money, and let everything downstream use that
value. Questions like this — where does this responsibility live? — are most of
what decomposition actually decides.

## Your turn

In `receipt.py`, for items given as `[(name, quantity, unit_price), ...]`:

- `line_total(quantity, price)` — rounded to 2 decimals
- `subtotal(items)`
- `tax(amount, rate=0.10)` — rounded to 2 decimals
- `total(items)` — subtotal plus tax
- `format_receipt(items)` — the lines above, joined with newlines, each item as
  `"<name> <qty> x <price> = <line total>"` and the three summary rows as
  `"SUBTOTAL <amount>"`, `"TAX <amount>"`, `"TOTAL <amount>"`, with amounts to
  two decimals
