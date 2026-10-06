---
title: "Paper 1: numbers, strings and lists"
summary: The arithmetic, slicing and mutability facts the certification asks about, and the edge cases it likes to hide in them.
order: 1
files: [basics.py]
run: python -i basics.py
hints:
  - "`/` always gives a float, even for `6 / 3`. `//` floors *towards negative infinity*, so `-7 // 2` is `-4`, not `-3`. The remainder follows: `a == (a // b) * b + a % b` always holds."
  - "A slice never raises. `word[:3]` on a two-letter word gives the whole thing, and `word[::-1]` reverses. `word[::2]` takes every other character starting at 0."
  - "Assigning to a slice can change the list's length: `values[1:4] = [0, 0]` replaces three items with two."
  - "Build the matrix with a nested comprehension: `[[r * cols + c for c in range(cols)] for r in range(rows)]`."
---

This paper covers the first section of the syllabus — the "informal
introduction" — which is worth six of the forty questions. The material looks
easy, and that is exactly why it is worth being precise about.

## Division has three operators

```pycon
>>> 7 / 2       # true division, always a float
3.5
>>> 6 / 2       # even when it divides exactly
3.0
>>> 7 // 2      # floor division
3
>>> -7 // 2     # floor means towards minus infinity, not towards zero
-4
>>> 7 % 2       # remainder
1
>>> 2 ** 10     # power
1024
```

`6 / 3` is `2.0`, not `2`. The exam likes that one.

Floor division floors **towards negative infinity**, not towards zero:

| Expression | Result | |
| --- | --- | --- |
| `7 // 2` | `3` | |
| `-7 // 2` | `-4` | not `-3` |
| `7 % 2` | `1` | |
| `-7 % 2` | `1` | the sign follows the **divisor** |

The identity `a == (a // b) * b + a % b` holds for every pair, which is the
reason for both oddities.

## Strings are immutable, and slices are forgiving

```pycon
>>> word = "Python"
>>> word[0]
'P'
>>> word[-1]       # negative counts from the end
'n'
>>> word[0:2]      # start included, end excluded
'Py'
>>> word[:2]       # omitted start means 0
'Py'
>>> word[2:]       # omitted end means len
'thon'
>>> word[::-1]     # negative step reverses
'nohtyP'
```

`word[0] = "J"` raises `TypeError` — strings cannot be changed in place. But
indexing out of range raises `IndexError` while **slicing out of range does
not**: `word[10:20]` is just `''`. One raises, the other shrugs.

## Lists are the mutable counterpart

Everything above works on lists, and slices can also be assigned:

```pycon
>>> values = [1, 2, 3, 4, 5]
>>> values[1:4] = [0, 0]
>>> values                 # three items replaced by two: the list got shorter
[1, 0, 0, 5]
```

A nested list is a list of lists, and `matrix[1][2]` reads row 1, column 2.

## Your turn

In `basics.py`:

- `arithmetic_facts(a, b)`: a dict with keys `quotient`, `floor`, `remainder`
  and `power`, holding `a / b`, `a // b`, `a % b` and `a ** b`.
  `arithmetic_facts(7, 2)` is
  `{"quotient": 3.5, "floor": 3, "remainder": 1, "power": 49}`.
- `slice_word(word)`: a tuple of four slices of the word, in this order: its
  first three characters, its last three, the whole word reversed, and every
  second character starting with the first. `slice_word("python")` is
  `("pyt", "hon", "nohtyp", "pto")`.
- `replace_slice(values)`: replace the items at indexes 1, 2 and 3 of the
  list with two zeros. Change the list you were given and return that same
  list, not a copy: `[10, 11, 12, 13, 14]` becomes `[10, 0, 0, 14]`.
- `build_matrix(rows, cols)`: a list of `rows` lists, each `cols` long,
  numbered row by row from 0, so that `matrix[r][c] == r * cols + c`.
  `build_matrix(2, 3)` is `[[0, 1, 2], [3, 4, 5]]`.
