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

## Generator expressions

With round brackets you get a lazy generator instead of a list. Functions
like `sum`, `any`, `all`, `max` and `"".join` accept one directly:

```python
sum(n * n for n in range(1000))
any(ch.isdigit() for ch in password)
```

## When not to

A comprehension is for building a collection. If you need several steps,
`try`/`except`, or side effects like printing, write the loop. Two `for`
clauses is about the limit of readable.

## Your turn

In `comprehensions.py`, write each as a single `return` of a comprehension:

- `evens_squared(numbers)`: squares of the even numbers, in order
- `lengths(words)`: a dict from each word to its length
- `flatten(grid)`: a list of lists into one list: `[[1, 2], [3]]` gives `[1, 2, 3]`
- `multiplication_table(n)`: an n by n grid where row `i`, column `j` holds
  `(i + 1) * (j + 1)`: `multiplication_table(2)` gives `[[1, 2], [2, 4]]`
