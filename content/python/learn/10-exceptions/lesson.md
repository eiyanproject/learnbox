---
title: Errors and exceptions
summary: Read a traceback, catch what you expect, raise your own errors with useful messages.
order: 10
files: [errors.py]
run: python -i errors.py
hints:
  - "`safe_divide`: `try: return a / b` then `except ZeroDivisionError: return None`."
  - "`parse_age`: `int(text)` raises `ValueError` for non-numbers. Let it, or catch it and `raise ValueError(...)` with your own message. Then check the range and `raise ValueError(\"age out of range\")`."
  - "`total_valid_prices`: loop, `try: total += float(item)`, `except ValueError: skipped += 1`, and return both."
  - "`withdraw` must check before changing anything: `if amount <= 0: raise ValueError(...)`, `if amount > balance: raise InsufficientFunds(...)`."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **exception** | an object describing an error: its kind and a message |
| **raise** | signal an exception; normal flow stops at that point |
| **catch** (handle) | deal with an exception in an `except` block instead of letting it stop the program |
| **traceback** | the report printed when nothing catches an exception; read it from the bottom up |
| **call stack** | the chain of function calls that led to a line; the traceback lists it, innermost call last |
| **`<module>`** | what a traceback calls the top level of a file, outside any function |
| **exception type** | the kind of error, such as `ValueError`; `except` catches only the type it names |
| **handler** | an `except` block; at most one runs |
| **bare `except:`** | an `except` with no type, catching everything; almost always a mistake |
| **class** | a definition of a new type (the next lesson); here, a recipe for a custom exception |
| **custom exception** | your own exception type, based on `Exception`: `class OutOfStock(Exception):` |
| **look before you leap** | checking first that an operation is safe |
| **easier to ask forgiveness than permission** | trying the operation and handling the error if it comes |
| **balance** | the money in an account |

### Python keywords and functions

| Name | What it does |
|---|---|
| `try:` | runs the risky code |
| `except SomeError:` | runs when the `try` block raised that type |
| `except SomeError as e:` | the same, with the exception object in `e`; `str(e)` is its message |
| `else:` | runs only if the `try` block raised nothing |
| `finally:` | always runs last, error or not; for clean-up |
| `raise ValueError("message")` | creates an exception with a message and raises it, ending the function |
| `Exception` | the base type that custom exceptions are built on |
| `pass` | does nothing; the class needs nothing extra |
| `int(text)`, `float(text)` | convert text to a number, raising `ValueError` when it is not one |
| `round(x, 2)` | rounds to 2 decimals |

### Errors

| Error | Typical cause |
|---|---|
| `ValueError` | right type, wrong value: `int("abc")` |
| `TypeError` | wrong type for the operation: `"2" + 2` |
| `NameError` | a name that has not been defined, often a typo |
| `KeyError` | a dict key that is not there |
| `IndexError` | a list position past the end |
| `ZeroDivisionError` | dividing by zero |
| `FileNotFoundError` | opening a file that is not there |
| `AttributeError` | a method or attribute the value does not have: `[1, 2].push(3)` |
| `InsufficientFunds` | this lesson's own exception: withdrawing more than the balance |

---

When a line of code cannot do its job, for example because it divides by
zero or asks for a dict key that is not there, Python **raises an
exception**. An exception is an object that describes the problem: what kind
of error it is, and a message. Raising it stops the normal flow of the
program at that point.

The exception then travels back up through the function calls that led to
that line, looking for code that has said "I can deal with this kind of
error" (you will see how below). If nothing catches it, the program stops and
Python prints a **traceback**: a report of where the program was when the
error happened.

```pytb
Traceback (most recent call last):
  File "shop.py", line 7, in <module>
    total = checkout(cart)
  File "shop.py", line 3, in checkout
    return price / quantity
ZeroDivisionError: division by zero
```

Read a traceback **from the bottom up**. The last line names the error and
says what happened; the lines above it show where, with the innermost call
last.

In this one, the bottom line says a division by zero happened. Above it, the
lines come in pairs: a location (file, line number and the function it was
in) and the line of code itself. The last pair is where the error actually
happened, line 3 inside `checkout`. The pair above that shows who called
`checkout`: line 7, at the top level of the file, which Python calls
`<module>`. So the story, read upwards, is: line 7 called `checkout`, and
inside it line 3 divided by zero.

The line that raised the error is not always the line with the bug. Here the
real question is why `quantity` was zero, and the answer may be in the code
that called `checkout`. The traceback tells you where to start looking.

## Common exceptions

Each kind of error has its own exception type, and the name usually tells
you what went wrong:

| Exception | Typical cause |
|---|---|
| `ValueError` | right type, wrong value: `int("abc")` is given a string, as it should be, but not one that holds a number |
| `TypeError` | wrong type for the operation: `"2" + 2` tries to add text to a number |
| `NameError` | a name that has not been defined, often a typo |
| `KeyError` | a dict key that is not there |
| `IndexError` | a list position past the end |
| `ZeroDivisionError` | dividing by zero |
| `FileNotFoundError` | opening a file that is not there |
| `AttributeError` | using a method or attribute a value does not have: `[1, 2].push(3)` (lists have `append`, not `push`) |

## try and except

To deal with an error yourself instead of letting it stop the program, put
the risky code in a `try` block, and say what to do about a particular kind
of error in an `except` block. Catch an exception you expect and can do
something sensible about:

```python
for text in ["3", "abc"]:
    try:
        quantity = int(text)
    except ValueError:
        quantity = 1
    print(text, "->", quantity)
```

```output
3 -> 3
abc -> 1
```

Here is what happens. Python runs the `try` block. If `text` holds a number,
`int()` succeeds, the `except` block is skipped, and the program carries on.
If `text` is something like `"abc"`, `int()` raises `ValueError`. The rest
of the `try` block is skipped, Python sees that the `except` names
`ValueError`, runs that block instead, and then carries on after it as if
nothing had gone wrong. Here, an unreadable quantity becomes 1.

An `except` only catches the type it names. If the `try` block raises some
other kind of exception, it passes straight through and carries on up as if
the `try` were not there.

You can have several `except` blocks for different errors, plus two optional
extras: `else`, which runs only if the `try` block finished without raising
anything, and `finally`, which always runs last, whether there was an error
or not:

```python
def compute(data, key, count):
    try:
        value = data[key] / count
    except KeyError:
        value = 0
    except ZeroDivisionError:
        value = None
    else:
        print("computed fine")
    finally:
        print("done either way")
    return value

data = {"a": 10}
print(compute(data, "a", 2))     # no error
print(compute(data, "b", 2))     # missing key
print(compute(data, "a", 0))     # division by zero
```

```output
computed fine
done either way
5.0
done either way
0
done either way
None
```

In order, for each call:

1. The `try` block runs.
2. If it raises, the rest of the `try` block is skipped, and the first
   `except` whose type matches runs. At most one handler runs.
3. If it does not raise, the `else` block runs instead.
4. Either way, `finally` runs last.

So with key `"a"` and count 2 there is no error, `else` prints "computed
fine", and the value is 5.0. With the missing key `"b"`, the `KeyError`
handler runs and the value is 0. With count 0, the `ZeroDivisionError`
handler runs and the value is `None`. In all three cases, "done either way"
is printed. `finally` is for
clean-up that must happen no matter what, such as closing a connection.

When you want to look at the error itself, add `as` and a name:
`except ValueError as e:` puts the exception object in `e`, and `str(e)` is
its message:

```pycon
>>> try:
...     int("abc")
... except ValueError as e:
...     print("could not convert:", e)
...
could not convert: invalid literal for int() with base 10: 'abc'
```

Catch the specific exception you expect. It is possible to write a bare
`except:` with no type, which catches everything, but that is almost always a
mistake. It also catches errors you never meant to handle: a typo in a
variable name (a `NameError`) is silently treated the same as bad input, so
the bug hides instead of being reported. It even catches Ctrl+C, so you
cannot stop the program. Name the error you expect, and let the rest show
up.

## Raising your own

Your own functions can raise exceptions too, with the `raise` statement.
Do this when a function is given something it cannot sensibly work with.
Returning a made-up value would let the problem slip through unnoticed;
raising stops it right where it is first spotted, with a message saying why.
`raise` ends the function immediately, like `return`, except that nothing is
returned and the exception travels up to the caller:

```pycon
>>> def set_volume(level):
...     if not 0 <= level <= 10:
...         raise ValueError(f"volume must be 0-10, got {level}")
...     return level
...
>>> set_volume(11)
Traceback (most recent call last):
  ...
ValueError: volume must be 0-10, got 11
```

`ValueError(...)` creates the exception object, with your message inside it,
and `raise` throws it. Pick the built-in type that fits: `ValueError` for a
bad value, `TypeError` for the wrong kind of value. A good message says what
was expected and what arrived, so whoever reads the traceback knows what to
fix without opening your code.

## Custom exception types

Sometimes no built-in type says exactly what went wrong, or a caller needs
to catch *your* error without accidentally catching other `ValueError`s. Then
you can create a new exception type of your own. It is a short **class**
(classes are the next lesson; for now, read this as a recipe) that is based
on Python's `Exception`, written in brackets after the name:

```pycon
>>> class OutOfStock(Exception):
...     pass
...
>>> raise OutOfStock("no mangoes left")
Traceback (most recent call last):
  ...
OutOfStock: no mangoes left
```

`pass` means the class needs nothing extra: everything it needs, such as
holding a message, comes from `Exception`. Callers can now catch it by name
with `except OutOfStock:`, and a reader of the traceback sees exactly what
went wrong. Exception names conventionally use capitals for each word, like
the built-in ones.

## Checking before, or asking forgiveness

There are two ways to deal with something that might fail. You can check
first and only go ahead if it is safe ("look before you leap"), or go ahead
and handle the error if it comes ("easier to ask forgiveness than
permission"):

```python
d = {"apples": 3}
key = "pears"

# check first
if key in d:
    value = d[key]
else:
    value = 0
print(value)

# try it, and handle the error
try:
    value = d[key]
except KeyError:
    value = 0
print(value)
```

```output
0
0
```

Both give 0 for a missing key.

Both styles are fine, and both appear in real Python code. Python programmers
often prefer trying, for two reasons. The check can repeat work the real
operation is about to do anyway. And a check can go stale: if another program
deletes a file between your "does it exist?" check and your opening it, the
open still fails, so you need the `try` regardless.

## Your turn

In `errors.py`, write:

- `safe_divide(a, b)`: `a / b`, or `None` when `b` is zero. Use
  `try`/`except` rather than an `if`, for the practice.
- `parse_age(text)`: the text as an `int`, so `parse_age("42")` is `42`. Raise
  `ValueError` if the text is not a whole number (`"abc"`, `"4.5"`), or if
  the number is below 0 or above 150 (`"-1"`, `"200"`). Note that `int()`
  already raises `ValueError` for text that is not a whole number, so you may
  let that error pass through; you only need your own `raise` for the
  range check.
- `total_valid_prices(items)`: `items` is a list of strings. Add up every one
  that `float()` can convert and skip the rest. Return two values: the total
  rounded to 2 decimals, and how many items were skipped.
  `total_valid_prices(["1.50", "abc", "2", ""])` returns `(3.5, 2)`: `"abc"`
  and the empty string cannot be converted, so they are the two skipped.
- `withdraw(balance, amount)`: return the new balance, so `withdraw(100, 30)`
  is `70`. Raise `ValueError` if `amount` is not positive (that is, zero or
  less), and raise the `InsufficientFunds` exception that is already defined
  in `errors.py` if the amount is more than the balance. Withdrawing exactly
  the whole balance is allowed.
