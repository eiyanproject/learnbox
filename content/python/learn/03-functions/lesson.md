---
title: Functions
summary: Package a calculation under a name, give it inputs, and return a result.
order: 3
files: [functions.py]
run: python -i functions.py
hints:
  - "A function without `return` gives back `None`. Every function here needs a `return`."
  - "`def greet(name, greeting=\"Hello\"):` makes `greeting` optional. Build the text with an f-string."
  - "For `bmi`, the formula is `weight_kg / height_m ** 2`. `**` happens before `/`, then `round(..., 1)`."
  - "For `split_bill`: `share = round(total / people, 2)`, then `return share, round(total - share * people, 2)`."
---

A **function** is a named block of code. You define it once and call it as
often as you like:

```python
def area(width, height):
    return width * height

print(area(3, 4))     # 12
print(area(10, 2))    # 20
```

- `def` starts the definition; `width` and `height` are **parameters**.
- The indented lines are the **body**. Python uses indentation (4 spaces)
  instead of braces to mark blocks.
- `return` hands a value back to whoever called the function, and ends it.

## print is not return

This trips up almost everyone once:

```python
def add_print(a, b):
    print(a + b)

def add_return(a, b):
    return a + b

x = add_print(2, 3)    # shows 5, but x is None
y = add_return(2, 3)   # shows nothing, y is 5
```

`print` shows something to a human. `return` gives a value to the code.
Tests, and other functions, can only use what you `return`.

## Default values and keyword arguments

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

greet("Ana")                        # 'Hello, Ana!'
greet("Ana", "Hi")                  # 'Hi, Ana!'
greet(greeting="Yo", name="Ana")    # by name, in any order
```

The `f"..."` is an **f-string**: anything inside `{}` is evaluated and put
into the text.

## Returning more than one value

Separate the values with commas, and unpack them where you call it:

```python
def min_max(a, b):
    if a < b:
        return a, b
    return b, a

low, high = min_max(9, 4)    # low = 4, high = 9
```

## Docstrings

A string on the first line of a function describes it. Try `help(area)` at
the `>>>` prompt.

```python
def area(width, height):
    """Area of a rectangle."""
    return width * height
```

## Your turn

Write the four functions in `functions.py`. `pass` means "do nothing yet";
replace it.

- `square(n)` returns `n` times `n`
- `greet(name, greeting="Hello")` returns text like `"Hello, Ana!"`
- `bmi(weight_kg, height_m)` returns weight divided by height squared, **rounded to 1 decimal place**
- `split_bill(total, people)` returns two values: each person's share rounded
  to 2 decimals, and the amount left over after that rounding,
  `round(total - share * people, 2)`
