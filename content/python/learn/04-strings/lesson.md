---
title: Strings
summary: Index, slice, search and reshape text with Python's string methods.
order: 4
files: [strings.py]
run: python -i strings.py
hints:
  - "`initials`: split the name into words with `.split()`, take `word[0]` of each, join them and `.upper()` the result. A loop is fine, and so is `\"\".join(...)`."
  - "`is_palindrome`: clean the text first. Keep only letters with `ch.isalpha()`, lower-case it, then compare it with its reverse `text[::-1]`."
  - "`mask_card`: `\"*\" * (len(number) - 4) + number[-4:]`."
  - "`slugify`: `.strip()`, `.lower()`, then `\"-\".join(text.split())` turns any run of spaces into a single dash."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **string** | Python's type for text (`str`) |
| **character** | one letter, digit, space or punctuation mark; `"Hi 5!"` has five |
| **sequence** | values stored in order, each with a numbered position; strings and lists are sequences |
| **index** | a position number in square brackets, `word[0]`; counting starts at 0 |
| **negative index** | counts from the end: `word[-1]` is the last character |
| **slice** (`[start:stop]`) | a new string from `start` up to, but not including, `stop` |
| **step** (`[start:stop:step]`) | how far a slice moves each time; `[::-1]` walks backwards, reversing |
| **immutable** | cannot be changed in place; you build a new string instead |
| **method** | a function that belongs to a value, called with a dot: `s.upper()` |
| **whitespace** | spaces, tabs and newlines |
| **list** | several values in square brackets, `['a', 'b']` (a later lesson) |
| **concatenate** | join strings end to end with `+` |
| **loop** | code that repeats its block, here once per character (a later lesson) |
| **format specification** | instructions after a colon inside an f-string's braces: `{price:.2f}` |
| **fixed-point** (`.2f`) | written with exactly that many decimals |
| **palindrome** | text that reads the same backwards |

### Python operators, functions and methods

| Name | What it does |
|---|---|
| `s[i]`, `s[a:b]`, `s[a:b:step]` | one character; a slice; a slice with a step |
| `s.strip()` | removes whitespace at both ends |
| `s.lower()`, `s.upper()` | the text in lower case; in upper case |
| `s.replace(old, new)` | every `old` replaced by `new` |
| `s.split(sep)` | breaks the text into a list at each `sep`; with no argument, at any whitespace, dropping empty pieces |
| `glue.join(pieces)` | joins a list of strings with `glue` between them: `"-".join(["a", "b"])` is `'a-b'` |
| `s.startswith(text)` | `True` if `s` begins with `text` |
| `s.count(text)` | how many times `text` appears |
| `s.find(text)` | the first position of `text`, or `-1` if absent |
| `s.isalpha()`, `s.isdigit()`, `s.isspace()` | `True` if every character is a letter; a digit; whitespace (`False` for an empty string) |
| `a in b` | `True` if `a` appears anywhere inside `b` |
| `len(s)` | the number of characters |
| `+`, `*` on strings | join two strings; repeat a string: `"ab" * 3` is `'ababab'` |
| `str(x)` | converts a value to text, so it can be joined with `+` |
| `for ch in s:` | runs the block once per character, with `ch` set to it |
| `f"{x:.2f}"`, `{x:>5}`, `{x:.0%}` | two decimals; right-aligned in 5 characters (`<` left, `^` centre); as a percentage |

### Errors

| Error | Means |
|---|---|
| `IndexError` | an index past the end of the string (a slice past the end is not an error) |
| `TypeError` | an operation on the wrong type, such as `"Level " + 3` |

---

Almost every program handles text: names, messages, file contents, web
pages. Python's type for text is the string, and it comes with a large set
of tools for cutting text up, searching it and reshaping it, so you rarely
have to do those jobs character by character yourself.

A string is a **sequence** of characters: the characters are stored in order,
and each one has a numbered position. Letters, digits, spaces and punctuation
are all characters, so `"Hi 5!"` is five characters long. Python has other
sequence types too, such as the lists you meet later, and most things that
work on one sequence work on all of them. What you learn here carries over.

## Indexing and slicing

Square brackets after a string pick out part of it. A single number is an
**index** and gives you one character. Positions start at 0, not 1, so the
first character is `[0]` and the second is `[1]`. Negative positions count
from the end: `[-1]` is the last character, `[-2]` the one before it.

```pycon
>>> word = "learnbox"
>>> word[0]
'l'
>>> word[-1]
'x'
>>> word[0:5]    # start is included, stop is not
'learn'
>>> word[5:]     # leave out stop to go to the end
'box'
>>> word[:5]     # leave out start to begin at 0
'learn'
>>> word[::-1]   # a step of -1 walks backwards
'xobnrael'
```

`[start:stop]` with a colon is a **slice**: it gives you a new string made of
several characters. The start position is included and the stop position is
not, so `word[0:5]` is positions 0, 1, 2, 3 and 4. It helps to picture the
positions as sitting *between* the characters:

```text
  l   e   a   r   n   b   o   x
0   1   2   3   4   5   6   7   8
```

`word[0:5]` is everything between mark 0 and mark 5. A nice result of this
rule is that `stop - start` is the length of the slice, and `word[:5]` plus
`word[5:]` always gives back the whole word.

A third number, `[start:stop:step]`, is the step: how far to move each time.
A step of 2 takes every other character, and a step of -1 walks backwards from
the end, which is the usual Python way to reverse a string.

An index past the end is an error, but a slice past the end is not; it stops
quietly at the end:

```pycon
>>> word[20]
Traceback (most recent call last):
  ...
IndexError: string index out of range
>>> word[5:20]
'box'
```

Strings cannot be changed in place: once a string exists, its characters
stay as they are. `word[0] = "L"` is an error. You build a new string
instead, for example `"L" + word[1:]`, and point a variable at that.

## Common methods

A **method** is a function that belongs to a value. You call it by writing
the value, a dot, and the method's name, like `s.upper()`, and it works on
the value before the dot. Strings come with dozens of them. Because a string
can never change, none of these methods change the original; each returns a
new string, and `s` itself is the same afterwards. To keep a result, assign
it: `s = s.strip()`.

```pycon
>>> s = "  Hello, World  "
>>> s.strip()              # trim spaces at both ends
'Hello, World'
>>> s.lower()
'  hello, world  '
>>> s.upper()
'  HELLO, WORLD  '
>>> s.replace("World", "Python")
'  Hello, Python  '
>>> "a,b,c".split(",")
['a', 'b', 'c']
>>> "one  two".split()     # no argument: split on any whitespace
['one', 'two']
>>> "-".join(["a", "b"])   # the opposite of split
'a-b'
>>> "hello".startswith("he")
True
>>> "hello".count("l")
2
>>> "hello".find("l")      # the first position...
2
>>> "hello".find("z")      # ...or -1 if it is not there
-1
```

`split()` breaks a string into a **list** of smaller strings (lists are
covered properly later; for now, a list is several values in square
brackets). With an argument, it cuts at every place that text appears. With no
argument, it cuts at any run of spaces, tabs or newlines and drops empty
pieces, which is usually what you want for words. `join()` goes the other way:
the string before the dot is the glue that is placed between the pieces.

Some methods answer a yes-or-no question about what a string contains. They
return `True` only if **every** character in the string passes, and `False`
for an empty string:

```pycon
>>> "a".isalpha()
True
>>> "7".isdigit()
True
>>> " ".isspace()
True
>>> "abc1".isalpha()     # the 1 is not a letter
False
```

## in and len

```pycon
>>> "box" in "learnbox"
True
>>> len("learnbox")
8
```

`in` checks whether one string appears anywhere inside another, and gives
`True` or `False`. `len()` gives the number of characters. Since positions
start at 0, the last valid index is always `len(word) - 1`.

## Joining and repeating

`+` sticks strings together end to end, and `*` repeats a string a number of
times:

```pycon
>>> "learn" + "box"
'learnbox'
>>> "ab" * 3
'ababab'
>>> "=" * 20
'===================='
```

`+` only joins a string to another string. Joining a number to text is an
error until you convert the number with `str()`, or use an f-string:

```pycon
>>> "Level " + 3
Traceback (most recent call last):
  ...
TypeError: can only concatenate str (not "int") to str
>>> "Level " + str(3)
'Level 3'
```

## Looping over characters

```python
for ch in "abc":
    print(ch)
```

```output
a
b
c
```

The loop runs its indented body once for each character, with `ch` set to
that character each time. You will see `for` loops properly in a later
lesson; for now, this is enough to go through a string one character at a
time.

## Formatting numbers inside f-strings

Inside an f-string's braces, a colon after the value starts a **format
specification**: instructions for how the value should be written out. The
value itself is not changed, only the text produced from it.

```pycon
>>> price = 3.5
>>> f"{price:.2f}"      # two decimals
'3.50'
>>> f"{42:>5}"          # right-aligned in 5 characters
'   42'
>>> f"{0.256:.0%}"      # as a percentage, no decimals
'26%'
```

Reading them: `.2f` means "a fixed-point number with 2 digits after the
decimal point" (it rounds, and pads with zeros when needed, so 3.5 becomes
`3.50`). `>5` means "right-align in a space 5 characters wide"; `<` would
align left and `^` would centre. `%` multiplies by 100 and adds a percent
sign, and `.0` before it asks for no decimal places.

## Your turn

In `strings.py`, write:

- `initials(full_name)`: the first letter of each word, upper-cased and
  joined with nothing in between: `initials("ada lovelace")` returns `"AL"`
- `is_palindrome(text)`: `True` if the text reads the same backwards,
  **ignoring case, spaces and punctuation**. `"Never odd or even"` is one:
  keep only its letters, lower-cased, and you get `neveroddoreven`, which is
  the same in both directions.
- `mask_card(number)`: the same string with every character except the last
  four replaced by `*`, so the result is as long as the input:
  `mask_card("4111111111111111")` returns `"************1111"`
- `slugify(title)`: the words in lower case, joined by single hyphens, with
  no spaces left anywhere: `slugify("  Hello World  From Python ")` returns
  `"hello-world-from-python"`
