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

```python
7 / 2       # 3.5   true division, always a float
7 // 2      # 3     floor division
7 % 2       # 1     remainder
2 ** 10     # 1024  power
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

```python
word = "Python"
word[0]        # 'P'
word[-1]       # 'n'      negative counts from the end
word[0:2]      # 'Py'     start included, end excluded
word[:2]       # 'Py'     omitted start means 0
word[2:]       # 'thon'   omitted end means len
word[::-1]     # 'nohtyP' negative step reverses
```

`word[0] = "J"` raises `TypeError` — strings cannot be changed in place. But
indexing out of range raises `IndexError` while **slicing out of range does
not**: `word[10:20]` is just `''`. One raises, the other shrugs.

## Lists are the mutable counterpart

Everything above works on lists, and slices can also be assigned:

```python
values = [1, 2, 3, 4, 5]
values[1:4] = [0, 0]      # [1, 0, 0, 5]  - the list got shorter
```

A nested list is a list of lists, and `matrix[1][2]` reads row 1, column 2.

## Your turn

In `basics.py`:

- `arithmetic_facts(a, b)`: a dict with keys `quotient`, `floor`, `remainder`
  and `power`, holding `a / b`, `a // b`, `a % b` and `a ** b`
- `slice_word(word)`: a tuple of the first three characters, the last three,
  the word reversed, and every other character from the start
- `replace_slice(values)`: replace items 1 through 3 of the list with two
  zeros, in place, and return the same list object
- `build_matrix(rows, cols)`: a nested list where `matrix[r][c] == r * cols + c`
