---
title: Making decisions
summary: if, elif and else; comparisons; and, or, not; and what Python treats as true.
order: 5
files: [decisions.py]
run: python -i decisions.py
hints:
  - "Check the most specific case first. For `grade`, test `score >= 90` before `score >= 80`."
  - "A year is a leap year if it divides by 4, except centuries, which must also divide by 400: `year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)`."
  - "`ticket_price`: handle the free cases first (under 3, or 65 and over), then the child price, then the weekend surcharge on the adult price."
  - "`describe_number` builds its answer from two separate questions: sign first, then even or odd. Zero is its own answer."
---

Programs choose what to do with `if`:

```python
temperature = 31

if temperature > 30:
    print("Hot")
elif temperature > 20:
    print("Warm")
else:
    print("Cool")
```

```output
Hot
```

Python checks each condition from the top and runs the **first** block that
is true, then skips the rest. `elif` and `else` are both optional.

## Comparisons

```python
a == b    # equal         (one = assigns, two compare)
a != b    # not equal
a < b     a <= b     a > b     a >= b
```

You can chain them the way you would on paper:

```python
if 18 <= age < 65:
    ...
```

## and, or, not

```python
if is_member and total > 100:
    discount = 0.1

if day == "Sat" or day == "Sun":
    weekend = True

if not logged_in:
    print("Please log in")
```

`and` binds tighter than `or`. When you mix them, add brackets so the reader
does not have to remember that.

## Truthiness

`if` accepts any value, not just `True` and `False`. These count as false:
`False`, `None`, `0`, `0.0`, `""` (empty string), `[]`, `{}`. Everything else
counts as true. `bool()` shows how a value would be treated:

```pycon
>>> bool(0), bool(""), bool([]), bool(None)
(False, False, False, False)
>>> bool(-1), bool("0"), bool([0])     # not empty, so true
(True, True, True)
```

```python
name = input("Name: ")
if not name:
    name = "stranger"
```

## Returning early

Inside a function, `return` ends it immediately. That often reads better than
deep nesting:

```python
def shipping(weight_kg):
    if weight_kg <= 0:
        return 0
    if weight_kg < 1:
        return 5
    return 5 + (weight_kg - 1) * 2
```

## The conditional expression

A one-line `if` that produces a value:

```python
label = "even" if n % 2 == 0 else "odd"
```

## Your turn

In `decisions.py`, write:

- `grade(score)`: `"A"` for 90 and up, `"B"` for 80 to 89, `"C"` for 70 to 79,
  `"D"` for 60 to 69, `"F"` below 60
- `is_leap_year(year)`: `True` or `False`. A year that divides by 4 is a leap
  year, with one exception: a year that also divides by 100 is only a leap
  year if it divides by 400 as well. So 2024 is a leap year, 1900 is not
  (it divides by 100 but not by 400), and 2000 is.
- `ticket_price(age, weekend)`: the price of one ticket. `weekend` is `True`
  or `False`.

  | Age | Price |
  |---|---|
  | under 3 | `0` |
  | 3 to 12 | `8` |
  | 13 to 64 | `15`, or `18` at the weekend |
  | 65 and over | `0` |

  Only the 13 to 64 price changes at the weekend: `ticket_price(12, True)` is
  still `8`.
- `describe_number(n)`: `"zero"` for 0. For any other whole number, two
  words: `positive` or `negative`, then `even` or `odd`.
  `describe_number(4)` is `"positive even"` and `describe_number(-9)` is
  `"negative odd"`.
