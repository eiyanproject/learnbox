---
title: "Boss: The function nobody wants to touch"
summary: One long function that works. Take it apart into named pieces and add a feature without breaking what it already does.
order: 4
files: [billing.py]
run: python -i billing.py
challenge:
  boss: true
  minutes: 30
  xp: 400
  requires:
    xp: 250
---

`bill()` has worked for years and nobody dares change it. Today it needs
discount codes, and you have half an hour.

## What it does now

`bill(lines)` takes order lines like `"2 x coffee @ 3.50"` and returns a
dict:

```python
bill(["2 x coffee @ 3.50", "1 x cake @ 4", "what?"])
# {"items": 2, "skipped": 1, "subtotal": 11.0, "total": 11.0}
```

Lines it cannot read are counted in `skipped` and otherwise ignored. Read
the function before you change it: it is the specification.

## The task

Split it into the four functions below, and make `bill` use them. Everything
`bill` does today must still be true afterwards.

- `parse_line(line)` turns one line into a dict:
  `parse_line("2 x coffee @ 3.50")` is
  `{"qty": 2, "name": "coffee", "price": 3.5}`. A line that `bill` skips
  today makes `parse_line` raise `ValueError`.
- `line_total(item)` is quantity times price for one parsed item.
- `subtotal(items)` is the sum of the line totals of a list of parsed items,
  rounded to 2 decimals.
- `discount(amount, code)` is the amount to take off, rounded to 2 decimals:

  | `code` | Discount |
  |---|---|
  | `None` | `0.0` |
  | `"TEN"` | 10% of the amount |
  | `"FIVER"` | `5.0`, but never more than the amount |
  | anything else | raises `ValueError` |

- `bill(lines, code=None)` now takes an optional code and returns one more
  key, `"discount"`, with `"total"` being the subtotal less the discount:

```python
bill(["2 x coffee @ 3.50", "1 x cake @ 4", "what?"], "TEN")
# {"items": 2, "skipped": 1, "subtotal": 11.0, "discount": 1.1, "total": 9.9}
```

Without a code, `"discount"` is `0.0` and the total is what it always was.
