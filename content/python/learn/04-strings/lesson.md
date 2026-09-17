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

```python
word = "learnbox"
word[0]      # 'l'
word[-1]     # 'x'
word[0:5]    # 'learn'   start is included, stop is not
word[5:]     # 'box'     leave out stop to go to the end
word[:5]     # 'learn'   leave out start to begin at 0
word[::-1]   # 'xobnrael' a step of -1 walks backwards
```

Strings cannot be changed in place. `word[0] = "L"` is an error; you build a
new string instead: `"L" + word[1:]`.

## Common methods

Methods are functions attached to a value, called with a dot. None of them
change the original; they return a new string.

```python
s = "  Hello, World  "
s.strip()              # 'Hello, World'   trim spaces at both ends
s.lower()              # '  hello, world  '
s.upper()              # '  HELLO, WORLD  '
s.replace("World", "Python")
"a,b,c".split(",")     # ['a', 'b', 'c']
"one  two".split()     # ['one', 'two']   no argument: split on any whitespace
"-".join(["a", "b"])   # 'a-b'            the opposite of split
"hello".startswith("he")   # True
"hello".count("l")         # 2
"hello".find("l")          # 2 (first position), -1 if missing
```

Tests about a character:

```python
"a".isalpha()   # True
"7".isdigit()   # True
" ".isspace()   # True
```

## in and len

```python
"box" in "learnbox"    # True
len("learnbox")        # 8
```

## Repeating and joining

```python
"ab" * 3               # 'ababab'
"=" * 20               # a line of 20 '='
```

## Looping over characters

```python
for ch in "abc":
    print(ch)
```

You will see `for` loops properly in a later lesson; for now, this is enough
to go through a string one character at a time.

## Formatting numbers inside f-strings

```python
price = 3.5
f"{price:.2f}"      # '3.50'   two decimals
f"{42:>5}"          # '   42'  right-aligned in 5 characters
f"{0.256:.0%}"      # '26%'
```

## Your turn

In `strings.py`, write:

- `initials("ada lovelace")` returns `"AL"`: the first letter of each word, upper-cased
- `is_palindrome(text)` returns `True` if the text reads the same backwards,
  **ignoring case, spaces and punctuation**: `"Never odd or even"` is one
- `mask_card("4111111111111111")` returns `"************1111"`: everything
  except the last four characters replaced with `*`
- `slugify("  Hello World  From Python ")` returns `"hello-world-from-python"`
