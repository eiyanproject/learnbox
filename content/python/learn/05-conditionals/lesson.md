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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **condition** | something that is either true or false: `temperature > 30` |
| **block** | the indented lines under a line ending in `:` |
| **comparison** | a question about two values that gives `True` or `False` |
| **dictionary order** | how strings compare: `"apple" < "banana"`; capitals and lower case differ |
| **chained comparison** | `18 <= age < 65`, the way you would write it on paper |
| **short-circuiting** | stopping as soon as the answer is known: in `x and y`, a false `x` means `y` is never checked |
| **truthy** / **falsy** | counts as true / false in a condition; falsy values are `False`, `None`, `0`, `0.0`, `""`, `[]`, `{}` |
| **empty string** (`""`) | a string with no characters; falsy |
| **dictionary** (`{}`) | a collection of key-value pairs (a later lesson) |
| **returning early** | ending a function with `return` as soon as a special case is handled |
| **nested** | one block inside another |
| **conditional expression** | a one-line choice between two values: `"even" if n % 2 == 0 else "odd"` |
| **leap year** | a year with 29 February: divisible by 4, except centuries not divisible by 400 |

### Python keywords, operators and functions

| Name | What it does |
|---|---|
| `if condition:` | runs its block only when the condition is true |
| `elif condition:` | "else if": checked only when every condition above it was false |
| `else:` | runs when every condition above was false |
| `==`, `!=` | equal; not equal |
| `<`, `<=`, `>`, `>=` | less than; less or equal; greater than; greater or equal |
| `=` | assignment, not comparison; in a condition it is a `SyntaxError` |
| `and` | true only when both sides are true |
| `or` | true when at least one side is true |
| `not` | flips true to false and false to true |
| `%` | remainder: `year % 4 == 0` means "divides by 4" |
| `bool(value)` | shows whether a value is truthy (`True`) or falsy (`False`) |
| `input(prompt)` | shows the prompt, waits for the user to type a line, and returns it as a string |
| `return` | ends the function at once with a value |

### Errors

| Error | Means |
|---|---|
| `SyntaxError` | not valid Python, such as `if x = 5:` (Python hints: "Maybe you meant '=='") |

---

So far every line of a program has run, in order. Real programs need to make
choices: do this if the order is over 100, do that if the password is wrong.
Python makes choices with `if`:

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

Each line that asks a question has the same shape: a keyword, a
**condition** (something that is either true or false), and a colon. The
indented lines under it are the block that runs if the answer is yes, in
the same way as a function body.

- `if` asks the first question.
- `elif` (short for "else if") asks another question, but only if every
  question above it was answered no. You can have as many as you need.
- `else` has no question. Its block runs when every question above was
  answered no.

Python checks the conditions from the top and runs the **first** block whose
condition is true, then skips the rest of the chain, even if later conditions
would also be true. Here 31 is above 30, so `Hot` is printed, and the
`> 20` check is never made, although 31 is above 20 too. That is why the
order of the checks matters.

`elif` and `else` are both optional. An `if` on its own runs its block or
skips it:

```python
temperature = 15
if temperature > 30:
    print("Hot")
print("done")
```

```output
done
```

15 is not above 30, so `Hot` is skipped and only the unindented line after
the `if` runs.

## Comparisons

A comparison asks a question about two values and gives back `True` or
`False`:

| Operator | Means |
|---|---|
| `a == b` | `a` is equal to `b` |
| `a != b` | `a` is not equal to `b` |
| `a < b` | `a` is less than `b` |
| `a <= b` | `a` is less than or equal to `b` |
| `a > b` | `a` is greater than `b` |
| `a >= b` | `a` is greater than or equal to `b` |

Watch the difference between `=` and `==`. One `=` assigns a value to a
name; two compare. Using `=` in a condition is a `SyntaxError`, so at least
Python catches the mistake for you, and recent versions even suggest the
fix:

```pycon
>>> x = 5
>>> if x = 5:
...     print("five")
Traceback (most recent call last):
  ...
SyntaxError: invalid syntax...
```

On screen, the message carries on with a hint along the lines of "Maybe you
meant '==' instead of '='?".

```pycon
>>> 3 == 3.0        # equal values, even of different number types
True
>>> "apple" == "Apple"   # strings must match exactly, capitals included
False
>>> "apple" < "banana"   # strings compare in dictionary order
True
```

You can chain comparisons the way you would on paper. `18 <= age < 65` means
"age is at least 18 and below 65":

```pycon
>>> age = 30
>>> 18 <= age < 65
True
>>> age = 70
>>> 18 <= age < 65      # 70 is at least 18, but not below 65
False
```

## and, or, not

These three words combine or flip conditions:

- `x and y` is true only when **both** are true.
- `x or y` is true when **at least one** is true.
- `not x` is true when `x` is false, and false when it is true.

```pycon
>>> is_member = True
>>> total = 80
>>> is_member and total > 100     # the second part is false
False
>>> day = "Sun"
>>> day == "Sat" or day == "Sun"  # the second part is true
True
>>> logged_in = False
>>> not logged_in
True
```

In an `if`, these read almost like English:

```python
if is_member and total > 100:
    discount = 0.1

if not logged_in:
    print("Please log in")
```

Each side of `and` and `or` must be a complete condition. A very common
mistake is to write `day == "Sat" or "Sun"`, which reads well in English but
means `(day == "Sat") or ("Sun")`. A non-empty string such as `"Sun"` always
counts as true (see Truthiness below), so the condition passes for every
day of the week, even ones that are not days at all:

```pycon
>>> day = "Mon"
>>> if day == "Sat" or "Sun":
...     print("weekend!")
...
weekend!
```

No error is reported, which is what makes this mistake hard to spot. Write
the comparison out on both sides: `day == "Sat" or day == "Sun"`.

Python also stops working out a condition as soon as the answer is known.
In `x and y`, if `x` is false the whole thing must be false, so `y` is never
checked; in `x or y`, if `x` is true, `y` is skipped. This is called
**short-circuiting**, and it lets you guard a risky check with a safe one:
`count > 0 and total / count > 10` never divides by zero.

When `and` and `or` are mixed, `and` is worked out first, the way `*` is
worked out before `+`. So `a or b and c` means `a or (b and c)`. Rather than
expect the reader to remember that, add the brackets yourself.

## Truthiness

`if` accepts any value, not only `True` and `False`. A value that counts as
true in a condition is called **truthy**, and one that counts as false is
**falsy**. The falsy values are: `False`, `None`, `0`, `0.0`, `""` (an empty
string), `[]` (an empty list) and `{}` (an empty dictionary). Everything else
is truthy. In short: zero and empty things are false; anything with
something in it is true. `bool()` shows how a value would be treated:

```pycon
>>> bool(0), bool(""), bool([]), bool(None)
(False, False, False, False)
>>> bool(-1), bool("0"), bool([0])     # not empty, so true
(True, True, True)
```

Note that `"0"` is true: it is a string with one character in it, not the
number zero. `[0]` is a list with one item in it, so it is true as well.

This makes "is there anything here?" checks short. `input()` shows a prompt,
waits for the user to type a line, and returns what they typed as a string.
If they press Enter without typing anything, it returns the empty string
`""`, which is falsy:

```python
name = input("Name: ")
if not name:
    name = "stranger"
print("Hello,", name)
```

`input()` waits for a person, so this one cannot run inside the lesson page.
Save it in a file and run it twice. Typing `Ana` the first time and nothing
the second gives:

```text
Name: Ana
Hello, Ana
Name:
Hello, stranger
```

## Returning early

Inside a function, `return` ends it immediately, wherever it is. You can use
that to deal with the special cases first and leave the function as soon as
you have the answer. The code that is left then only has to handle the normal
case, which often reads better than `if` blocks nested inside each other:

```pycon
>>> def shipping(weight_kg):
...     if weight_kg <= 0:
...         return 0
...     if weight_kg < 1:
...         return 5
...     return 5 + (weight_kg - 1) * 2
...
>>> shipping(0)
0
>>> shipping(0.5)
5
>>> shipping(3)
9
```

Reading it from the top: nothing to send costs 0, and the function ends
there. Otherwise, a parcel under 1 kg costs 5, and the function ends there.
Only a parcel of 1 kg or more reaches the last line, which charges 5 for the
first kilogram plus 2 for each kilogram after it: 3 kg is 5 + 2 * 2 = 9.
Because the earlier
`return`s have already dealt with the small cases, the last line needs no
`if` of its own.

## The conditional expression

Sometimes all an `if` does is choose between two values. Python has a
one-line form for that, which produces a value directly:

```pycon
>>> n = 7
>>> label = "even" if n % 2 == 0 else "odd"
>>> label
'odd'
```

Read it as English: label is `"even"` if `n` divides by 2, otherwise
`"odd"`. The condition sits in the middle, with the value for true on its
left and the value for false after `else`. Both parts are required. It does
the same job as this longer version, which also leaves `label` as `'odd'`:

```python
if n % 2 == 0:
    label = "even"
else:
    label = "odd"
```

Use the one-line form for short, simple choices. When either side needs real
work, the full `if` statement is clearer.

## Your turn

In `decisions.py`, write:

- `grade(score)`: `"A"` for 90 and up, `"B"` for 80 to 89, `"C"` for 70 to 79,
  `"D"` for 60 to 69, `"F"` below 60
- `is_leap_year(year)`: `True` or `False`. A year that divides by 4 is a leap
  year, with one exception: a year that also divides by 100 is only a leap
  year if it divides by 400 as well. So 2024 is a leap year, 1900 is not
  (it divides by 100 but not by 400), and 2000 is. "Divides by 4" means
  there is no remainder, which in Python is `year % 4 == 0`.
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
  words separated by a single space: `positive` or `negative`, then `even`
  or `odd`. (Negative numbers can be even or odd too: `-9 % 2` is `1` in
  Python, so the same `% 2` test works for them.)
  `describe_number(4)` is `"positive even"` and `describe_number(-9)` is
  `"negative odd"`.
