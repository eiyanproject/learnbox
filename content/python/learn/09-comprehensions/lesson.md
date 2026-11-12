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

In the loops lesson you built lists by starting with `[]` and appending
inside a `for` loop. That pattern is so common that Python has a shorter way
to write it. A **comprehension** builds a whole collection from a loop in one
expression: one piece of code that produces a value, which you can assign,
return or pass straight to a function. This loop:

```python
squares = []
for n in range(10):
    squares.append(n * n)
print(squares)
```

```output
[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

is the same as:

```python
squares = [n * n for n in range(10)]
print(squares)
```

```output
[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

Read it left to right as "`n * n`, for each `n` in `range(10)`". The square
brackets say "make a list". Inside them, the part before `for` is what goes
into the list for each item, and the `for ... in ...` part is the same loop
header you would write in an ordinary loop, without the colon. There is no
`append` and no empty list to start from; the comprehension does both.

The loop variable, `n` here, only exists inside the comprehension. After the
line has run, there is no `n` left over.

## Filtering

Add an `if` at the end to keep only some items. Items for which the
condition is false are skipped, so the result can be shorter than the
input:

```pycon
>>> [n for n in range(20) if n % 3 == 0]
[0, 3, 6, 9, 12, 15, 18]
>>> words = ["sky", "river", "tree", "ocean"]
>>> [w.upper() for w in words if len(w) > 3]
['RIVER', 'TREE', 'OCEAN']
```

To choose between two values for every item, the condition goes at the
front instead, as a conditional expression (the `x if condition else y`
form from the lesson on decisions):

```pycon
>>> ["even" if n % 2 == 0 else "odd" for n in range(4)]
['even', 'odd', 'even', 'odd']
```

The position of the `if` is what tells the two apart, and the two are often
mixed up:

- An `if` **at the end** is a filter. It decides *whether* an item goes in
  at all, and has no `else`.
- An `if ... else` **at the front** is part of the value. Every item goes in,
  and the condition decides *what* goes in for it. The `else` is required.

## Dict and set comprehensions

The same idea works with curly braces. With a `key: value` pair before the
`for`, you get a dict; with a single value, you get a set (which, as usual,
drops duplicates):

```pycon
>>> {name: len(name) for name in ["Ana", "Budi"]}
{'Ana': 3, 'Budi': 4}
>>> {word[0] for word in ["ant", "asp", "bee"]} == {"a", "b"}
True
```

(The set is compared rather than shown, because a set's printed order can
change between runs.)

## Without brackets: generator expressions

If you only want to feed the values into a function such as `sum()`,
`max()` or `any()`, you can leave out the square brackets and write the
comprehension directly inside the function's brackets. This is called a
**generator expression**. It produces the values one at a time as the
function asks for them, without building a whole list first:

```pycon
>>> sum(n * n for n in range(4))       # 0 + 1 + 4 + 9
14
>>> sum(1 for w in ["a", "", "b"] if w)   # count the non-empty strings
2
```

The second line is a handy counting trick: it adds up a 1 for every item
that passes the filter.

## Nested loops

Several `for` clauses run nested, in the order written. The first `for` is
the outer loop and the second is the inner loop, exactly as if you had
written one `for` inside the other:

```pycon
>>> [(x, y) for x in range(2) for y in range(3)]
[(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
```

As ordinary loops, that is:

```python
pairs = []
for x in range(2):
    for y in range(3):
        pairs.append((x, y))
print(pairs)
```

```output
[(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
```

`y` runs through all of its values for each single value of `x`, which is
why `x` stays at 0 for the first three pairs.

That gives one flat list. A comprehension can also sit *inside* another
one, which gives a list of lists, such as a grid:

```pycon
>>> [[0 for col in range(3)] for row in range(2)]
[[0, 0, 0], [0, 0, 0]]
```

Read that from the outside in. The **outer** comprehension makes the rows -
two of them, one per `row` - and the value it puts in for each row is the
whole **inner** comprehension, which makes the three values inside that row.
(The loop variables `col` and `row` are not used in the values here; the
loops are only there to repeat things the right number of times.)

The inner comprehension can use the outer loop variable, so the values can
depend on both:

```pycon
>>> [[row + col for col in range(3)] for row in range(2)]
[[0, 1, 2], [1, 2, 3]]
```

Row 0 gives `0+0, 0+1, 0+2`; row 1 gives `1+0, 1+1, 1+2`. If you are unsure
what a nested comprehension will do, write it as two ordinary `for` loops
first, get it right, and then fold it up.

## When not to

A comprehension is for building a collection, and nothing else. Write an
ordinary loop instead when:

- each item needs several steps, or temporary variables, to work out;
- you need `try`/`except` around part of the work (the next lesson);
- the point of the loop is a **side effect**, something it does rather than
  something it builds, such as printing or writing to a file. A comprehension
  used only for its side effects builds a list of `None`s that nobody wants.

Readability is the other limit. Two `for` clauses, or one `for` and an `if`,
is about as much as a reader can take in at a glance. Past that, the loop
version is easier to follow, and being short is not worth being hard to read.

## Your turn

In `comprehensions.py`, write each function body as a single `return`
statement whose value is a comprehension:

- `evens_squared(numbers)`: squares of the even numbers, in order:
  `[1, 2, 3, 4]` gives `[4, 16]`
- `lengths(words)`: a dict from each word to its length: `["hi", "there"]`
  gives `{"hi": 2, "there": 5}`
- `flatten(grid)`: turn a list of lists into one flat list holding all the
  items, in order: `[[1, 2], [3]]` gives `[1, 2, 3]`. This is the two-`for`
  form from "Nested loops": an outer loop over the rows, then an inner loop
  over the items in each row.
- `multiplication_table(n)`: the hardest one here, and a nested comprehension
  like the `row + col` example above. It returns the times table as an n by n
  grid: `multiplication_table(3)` gives `[[1, 2, 3], [2, 4, 6], [3, 6, 9]]`.
  The first row is 1 to n, the second row is the same numbers doubled, the
  third tripled. Counting rows and columns from 0, as `range` does, the
  number at row `i`, column `j` is `(i + 1) * (j + 1)`.
