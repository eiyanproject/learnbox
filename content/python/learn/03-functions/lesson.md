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

A **function** is a named block of code. You define it once and then **call**
it, by name, as often as you like. Instead of writing the same calculation
in five places, you write it once, give it a name, and use the name. If the
calculation ever needs fixing, there is only one place to fix it.

```python
def area(width, height):
    return width * height

print(area(3, 4))
print(area(10, 2))
```

```output
12
20
```

Piece by piece:

- `def` (short for define) starts the definition. Then comes the function's
  name, `area`, and in brackets its **parameters**, `width` and `height`:
  the names the function uses for the inputs it will be given.
- The line ends with a colon, `:`. Python uses a colon to say "a block
  follows".
- The indented lines under it are the **body**: the code that runs each time
  the function is called. Many languages mark a block with curly braces;
  Python uses indentation instead, and the indentation is required, not
  decoration. The convention is 4 spaces. The body ends at the first line
  that is no longer indented.
- `return` hands a value back to the code that called the function, and
  ends the function at that point. Any lines after a `return` that runs are
  skipped.

Defining a function does not run it. Python only notes that `area` now
exists. The body runs when a call happens: `area(3, 4)` runs the body with
`width` set to `3` and `height` set to `4`, and the call itself then stands
for the returned value, `12`, which `print()` shows. The values given in a
call, `3` and `4` here, are called **arguments**; the parameters are the
names they arrive under.

Variables created inside a function exist only while that call runs. Code
outside the function cannot see them; it only gets what is returned.

## print is not return

This trips up almost everyone at least once. Both of the functions below seem
to "give you" 5 at the prompt, but only one of them hands 5 back to your code.

(At the `>>>` prompt, typing a line that ends in `:` switches the prompt to
`...`, meaning Python is waiting for the rest of the block. Type the indented
lines, then press Enter on an empty `...` line to finish it.)

```pycon
>>> def add_print(a, b):
...     print(a + b)
...
>>> def add_return(a, b):
...     return a + b
...
>>> x = add_print(2, 3)    # shows 5...
5
>>> print(x)               # ...but x is None
None
>>> y = add_return(2, 3)   # shows nothing...
>>> y                      # ...but y is 5
5
```

`print` shows something to a human. `return` gives a value to the code.
Tests, and other functions, can only use what you `return`.

`None` is Python's value for "nothing here". A function that ends without
reaching a `return` gives back `None` automatically. That is why `x` above is
`None`: `add_print` showed 5 on the screen, then finished without returning
anything. The prompt does not display `None` on its own line, which is why
`x` had to be printed to see it.

## Default values and keyword arguments

```pycon
>>> def greet(name, greeting="Hello"):
...     return f"{greeting}, {name}!"
...
>>> greet("Ana")
'Hello, Ana!'
>>> greet("Ana", "Hi")
'Hi, Ana!'
>>> greet(greeting="Yo", name="Ana")    # by name, in any order
'Yo, Ana!'
```

`greeting="Hello"` gives the parameter a **default value**: if the caller
leaves that argument out, the parameter gets `"Hello"`. A parameter without a
default must always be given. Parameters with defaults have to come after the
ones without, which is why `greeting` is last.

Arguments are normally matched to parameters by position: the first argument
goes to the first parameter, and so on. Writing `name=value` in the call
instead matches by name, which is called a **keyword argument**. Keyword
arguments can come in any order, and they make a call easier to read when a
function takes several values.

The `f"..."` is an **f-string** (f for formatted). Anything inside `{}` in
it is worked out as Python code, and the result is put into the text at that
point. Without the `f` in front, the braces are ordinary characters and
the name inside them is not replaced:

```pycon
>>> name = "Ana"
>>> f"Hi, {name}!"
'Hi, Ana!'
>>> "Hi, {name}!"
'Hi, {name}!'
```

## Returning more than one value

Separate the values with commas after `return`, and unpack them where you
call the function:

```pycon
>>> def min_max(a, b):
...     if a < b:
...         return a, b
...     return b, a
...
>>> low, high = min_max(9, 4)
>>> low
4
>>> high
9
```

Strictly speaking the function still returns one value: `return a, b` packs
the two values into a **tuple**, a fixed group of values written in brackets.
`low, high = ...` then unpacks the tuple into two names, one value each. You
can see the tuple if you do not unpack it:

```pycon
>>> min_max(9, 4)
(4, 9)
```

Tuples get a lesson of their own later. For now, "return several values with
commas, unpack them with commas" is all you need.

## Docstrings

A string placed as the very first line of a function's body is its
**docstring**: a description of what the function does. Python stores it with
the function, and `help()` shows it. Try `help(area)` at the `>>>` prompt
(press `q` to leave the help screen). Triple quotes, `"""`, are used so the
description can run over several lines if it needs to.

```pycon
>>> def area(width, height):
...     """Area of a rectangle."""
...     return width * height
...
>>> area.__doc__
'Area of a rectangle.'
```

`area.__doc__` is where Python keeps the docstring; `help(area)` shows the
same text, laid out with the function's parameters above it. A function
without a docstring has `None` there.

## Your turn

Write the four functions in `functions.py`. Each one currently has `pass` as
its body. `pass` is a statement that does nothing; it is there because a
body cannot be empty. Replace it with your code.

- `square(n)` returns `n` times `n`: `square(4)` is `16`
- `greet(name, greeting="Hello")` returns text like `"Hello, Ana!"`. A second
  argument replaces the word Hello: `greet("Ana", "Welcome")` is
  `"Welcome, Ana!"`
- `bmi(weight_kg, height_m)` returns weight divided by height squared,
  **rounded to 1 decimal place**: `bmi(70, 1.75)` is `22.9`
- `split_bill(total, people)` splits a bill evenly and returns **two values**:

  1. the **share**: what each person pays, which is `total / people` rounded
     to 2 decimals
  2. the **leftover**: what is still unpaid after everyone has paid that
     share, which is `total - share * people`, also rounded to 2 decimals

  The leftover exists because the share was rounded. Split 100 between 3
  people and each pays `33.33`. Three of those come to 99.99, so 0.01 of the
  bill is left: `split_bill(100, 3)` returns `(33.33, 0.01)`. When the bill
  divides exactly, nothing is left: `split_bill(90, 3)` returns `(30.0, 0.0)`.
