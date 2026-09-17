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
counts as true.

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
- `is_leap_year(year)`: divisible by 4, except century years, which must also
  be divisible by 400 (2000 was a leap year, 1900 was not)
- `ticket_price(age, weekend)`: under 3 or 65 and over are free (`0`); ages 3
  to 12 pay `8`; everyone else pays `15`, plus `3` on weekends. Children's
  and free tickets have no weekend surcharge.
- `describe_number(n)`: `"zero"` for 0, otherwise `"positive even"`,
  `"negative odd"` and so on
