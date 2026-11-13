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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **paper** | one part of this exam-preparation section, matching a syllabus section |
| **syllabus** | the list of topics the certification covers |
| **true division** (`/`) | always gives a float, even `6 / 3` is `2.0` |
| **floor division** (`//`) | rounds down towards minus infinity: `-7 // 2` is `-4` |
| **remainder** (`%`) | what makes `a == (a // b) * b + a % b` true; its sign follows the divisor |
| **divisor** | the number you divide by |
| **power** (`**`) | `2 ** 10` is `1024` |
| **immutable** | cannot be changed in place, like a string |
| **index** / **negative index** | one position, from 0 / counting from the end |
| **slice** | `word[start:end:step]`: start included, end excluded; never raises |
| **step** | how far a slice moves; `[::2]` every other, `[::-1]` reversed |
| **mutable** | can be changed in place, like a list |
| **slice assignment** | `values[1:4] = [0, 0]` replaces a stretch, so the length can change |
| **nested list** (matrix) | a list of lists; `matrix[1][2]` is row 1, column 2 |
| **shared-row trap** | `[[0] * 3] * 2` repeats the **same** inner list; build rows with a comprehension |

### Python operators and functions

| Name | What it does |
|---|---|
| `/`, `//`, `%`, `**` | true division, floor division, remainder, power |
| `word[0]`, `word[-1]`, `word[:2]`, `word[2:]` | first; last; first two; from position 2 |
| `[[r * cols + c for c in range(cols)] for r in range(rows)]` | a matrix with a new list per row |
| `range(n)` | `0` to `n - 1` |

### Errors

| Error | Means |
|---|---|
| `TypeError` | assigning to a character of a string: `word[0] = "J"` |
| `IndexError` | an index out of range (a slice out of range is not an error) |

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
reason for both oddities. Python first decides that `//` rounds down, towards
minus infinity, so `-7 / 2 = -3.5` becomes `-4`. The remainder then has to be
whatever makes the identity true: `-4 * 2` is `-8`, and getting from `-8`
back to `-7` takes `+1`, so `-7 % 2` is `1`. With a negative divisor
everything flips: `7 // -2` is `-4` and `7 % -2` is `-1`, because
`-4 * -2 + -1` is `7`.

```pycon
>>> -7 // 2, -7 % 2
(-4, 1)
>>> 7 // -2, 7 % -2
(-4, -1)
>>> (-7 // 2) * 2 + (-7 % 2)      # the identity gives back -7
-7
```

(Some other languages, C and Java among them, round towards zero instead, so
`-7 / 2` is `-3` there and the remainder is `-1`. That difference is exactly
what the exam tests.)

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
not**: `word[10:20]` is `''`, an empty string. One raises, the other shrugs:

```pycon
>>> word[0] = "J"
Traceback (most recent call last):
  ...
TypeError: 'str' object does not support item assignment
>>> word[10]
Traceback (most recent call last):
  ...
IndexError: string index out of range
>>> word[10:20]
''
>>> word[:10]        # asking for more than there is gives what there is
'Python'
>>> word[::2]        # a step of 2: positions 0, 2, 4
'Pto'
```

The last line is the third slice number, the **step**. `[::2]` takes every
second character from the start, and `[::-1]` walks backwards from the end.

## Lists are the mutable counterpart

Everything above works on lists, and slices can also be assigned:

```pycon
>>> values = [1, 2, 3, 4, 5]
>>> values[1:4] = [0, 0]
>>> values                 # three items replaced by two: the list got shorter
[1, 0, 0, 5]
```

Assigning to a slice replaces that whole stretch of the list with the new
items, however many there are, so the list can grow or shrink. Assigning to a
single index replaces exactly one item and never changes the length.

A nested list is a list of lists, and `matrix[1][2]` reads row 1, column 2.

One classic trap: `[[0] * 3] * 2` looks like a 2 by 3 grid, but `* 2`
repeats the **same** inner list twice instead of making two lists. Changing
one row changes "both":

```pycon
>>> grid = [[0] * 3] * 2
>>> grid[0][0] = 9
>>> grid                       # both rows are one list
[[9, 0, 0], [9, 0, 0]]
>>> grid = [[0] * 3 for _ in range(2)]   # a new inner list per row
>>> grid[0][0] = 9
>>> grid
[[9, 0, 0], [0, 0, 0]]
```

## Your turn

In `basics.py`:

- `arithmetic_facts(a, b)`: a dict with keys `quotient`, `floor`, `remainder`
  and `power`, holding `a / b`, `a // b`, `a % b` and `a ** b`.
  `arithmetic_facts(7, 2)` is
  `{"quotient": 3.5, "floor": 3, "remainder": 1, "power": 49}`. The tests
  include negative numbers, where Python's own operators already give the
  right answers, so use them directly.
- `slice_word(word)`: a tuple of four slices of the word, in this order: its
  first three characters, its last three, the whole word reversed, and every
  second character starting with the first. `slice_word("python")` is
  `("pyt", "hon", "nohtyp", "pto")`. It must not fail on short words:
  `slice_word("hi")` is `("hi", "hi", "ih", "h")`.
- `replace_slice(values)`: replace the items at indexes 1, 2 and 3 of the
  list with two zeros. Change the list you were given and return that same
  list, not a copy: `[10, 11, 12, 13, 14]` becomes `[10, 0, 0, 14]`.
- `build_matrix(rows, cols)`: a list of `rows` lists, each `cols` long,
  numbered row by row from 0, so that `matrix[r][c] == r * cols + c`.
  `build_matrix(2, 3)` is `[[0, 1, 2], [3, 4, 5]]`. Each row must be a
  separate list (a test changes one row and checks the others did not
  change), so avoid the `* rows` trap above.
