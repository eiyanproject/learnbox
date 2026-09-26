---
title: Comprehensions
summary: Build lists, dicts and sets in one readable line, and know when a loop is clearer.
order: 9
files: [comprehensions.py]
run: python -i comprehensions.py
hints:
  - "`evens_squared`: `[n * n for n in numbers if n % 2 == 0]`."
  - "`lengths`: a dict comprehension, `{word: len(word) for word in words}`."
  - "`flatten`: two `for` clauses, in the same order you would nest the loops: `[x for row in grid for x in row]`."
  - "`multiplication_table(n)`: a list comprehension inside a list comprehension; the outer one makes rows, the inner one makes the values in a row."
---

A **comprehension** builds a collection from a loop in one expression. This
loop:

```python
squares = []
for n in range(10):
    squares.append(n * n)
```

is the same as:

```python
squares = [n * n for n in range(10)]
```

Read it left to right as "`n * n`, for each `n` in `range(10)`".

## Filtering

Add an `if` at the end to keep only some items:

```python
[n for n in range(20) if n % 3 == 0]      # [0, 3, 6, 9, 12, 15, 18]
[w.upper() for w in words if len(w) > 3]
```

To choose between two values for every item, the condition goes at the
front instead, as a conditional expression:

```python
["even" if n % 2 == 0 else "odd" for n in range(4)]
# ['even', 'odd', 'even', 'odd']
```

## Dict and set comprehensions

```python
{name: len(name) for name in ["Ana", "Budi"]}   # {'Ana': 3, 'Budi': 4}
{word[0] for word in ["ant", "asp", "bee"]}     # {'a', 'b'}
```

## Nested loops

Several `for` clauses run nested, in the order written:

```python
[(x, y) for x in range(2) for y in range(3)]
# [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
```

A comprehension can also sit inside another one to build a grid:

```python
[[0 for col in range(3)] for row in range(2)]
# [[0, 0, 0], [0, 0, 0]]
```

Read that from the outside in. The **outer** comprehension makes the rows - two
of them, one per `row` - and the **inner** one makes the three values inside
each row. The outer loop variable is in scope in the inner one, so the values
can depend on both:

```python
[[row + col for col in range(3)] for row in range(2)]
# [[0, 1, 2], [1, 2, 3]]
```

Row 0 gives `0+0, 0+1, 0+2`; row 1 gives `1+0, 1+1, 1+2`. If you are unsure
what a nested comprehension will do, write it as two ordinary `for` loops
first, get it right, and then fold it up.

## When not to

A comprehension is for building a collection. If you need several steps,
`try`/`except`, or side effects like printing, write the loop. Two `for`
clauses is about the limit of readable.

## Your turn

In `comprehensions.py`, write each as a single `return` of a comprehension:

- `evens_squared(numbers)`: squares of the even numbers, in order
- `lengths(words)`: a dict from each word to its length
- `flatten(grid)`: a list of lists into one list: `[[1, 2], [3]]` gives `[1, 2, 3]`
- `multiplication_table(n)`: the hardest one here, and a nested comprehension
  like the `row + col` example above. An n by n grid where row `i`, column `j`
  holds `(i + 1) * (j + 1)`, counting rows and columns from 0:
  `multiplication_table(2)` gives `[[1, 2], [2, 4]]`
