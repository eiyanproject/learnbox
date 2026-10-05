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

A string is a sequence of characters, and most things that work on sequences
work on strings.

## Indexing and slicing

Positions start at 0. Negative positions count from the end:

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

Strings cannot be changed in place. `word[0] = "L"` is an error; you build a
new string instead: `"L" + word[1:]`.

## Common methods

Methods are functions attached to a value, called with a dot. None of them
change the original; they return a new string.

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

Tests about a character:

```pycon
>>> "a".isalpha()
True
>>> "7".isdigit()
True
>>> " ".isspace()
True
```

## in and len

```pycon
>>> "box" in "learnbox"
True
>>> len("learnbox")
8
```

## Repeating and joining

```pycon
>>> "ab" * 3
'ababab'
>>> "=" * 20
'===================='
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

You will see `for` loops properly in a later lesson; for now, this is enough
to go through a string one character at a time.

## Formatting numbers inside f-strings

```pycon
>>> price = 3.5
>>> f"{price:.2f}"      # two decimals
'3.50'
>>> f"{42:>5}"          # right-aligned in 5 characters
'   42'
>>> f"{0.256:.0%}"      # as a percentage, no decimals
'26%'
```

## Your turn

In `strings.py`, write:

- `initials(full_name)`: the first letter of each word, upper-cased:
  `initials("ada lovelace")` returns `"AL"`
- `is_palindrome(text)`: `True` if the text reads the same backwards,
  **ignoring case, spaces and punctuation**. `"Never odd or even"` is one:
  keep only its letters, lower-cased, and you get `neveroddoreven`, which is
  the same in both directions.
- `mask_card(number)`: everything except the last four characters replaced
  with `*`: `mask_card("4111111111111111")` returns `"************1111"`
- `slugify(title)`: the words in lower case, joined by single hyphens, with
  no spaces left anywhere: `slugify("  Hello World  From Python ")` returns
  `"hello-world-from-python"`
