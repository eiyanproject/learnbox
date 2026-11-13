---
title: "Paper 1: the language and arrays"
summary: Types, indexing, operators and shape - the ground the rest of the exam stands on.
order: 1
files: [array_report.m, trim_outliers.m, interleave.m]
run: octave --no-gui --quiet --eval "disp(interleave([1 2 3], [4 5 6]))"
hints:
  - "A struct is built by assigning fields. The checks read r.n, r.mn, r.mx, r.avg and r.kind."
  - "`std(v)` of a constant vector is 0, which makes every element exactly on the boundary - decide whether that keeps them."
  - "`reshape([a(:)'; b(:)'], 1, [])` reads down the columns of a 2-row matrix, which is the interleaving."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **cumulative paper** | a test covering everything so far, with fewer hints |
| **one-based indexing** | the first element is `v(1)` |
| **`end`** (in an index) | the last position |
| **colon** | `1:n` builds a range; `v(:)` takes everything as a column |
| **element-wise** vs **matrix** operators | `.*` multiplies matching elements; `*` is matrix multiplication |
| **logical mask** | a true/false array that selects elements |
| **struct** | named fields in one value |
| **standard deviation** | how spread out values are |
| **outlier** | a value far from the rest |
| **interleave** | alternate elements of two arrays |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `octave --no-gui --quiet --eval "..."` | runs one line of MATLAB code in Octave, with no window and no banner, as Run does |

### MATLAB names

| Name | What it does |
|---|---|
| `class(x)`, `size(x, 1)`, `size(x, 2)` | type / rows / columns |
| `isequal(a, b)` | whether two arrays are equal |
| `v(v > 0)`, `sum(v > 0)` | select / count matches |
| `numel`, `min`, `max`, `mean`, `std` | count, extremes, average, standard deviation |
| `abs(x)` | absolute value |
| `reshape(M, 1, [])` | reshapes into a row |
| `[a; b]` | stacks rows |
| `struct('n', n, ...)` | builds a struct |
| `error('id:name', ...)` | throws with an identifier |

---

The first of four cumulative papers. Fewer hints than a lesson, on purpose: the
point is to find out what you can do without being led.

This paper covers the ground from **Environment** and **Beginner** — classes
and sizes, one-based indexing, `end` and the colon, element-wise against matrix
operators, logical masks, and the shape rules that decide what an expression
means.

Three things worth having straight before you start:

- `class` and `size` describe any value, and a scalar is a 1×1 array
- `.*` is element-wise and `*` is matrix multiplication; for square inputs both
  run and disagree
- a logical array used as a subscript selects; `sum` of it counts

```matlab
x = 7;
fprintf('%s %d %d\n', class(x), size(x, 1), size(x, 2));
A = [1 2; 3 4];
disp(isequal(A * A, A .* A))
v = [3 -1 4];
disp(v(v > 0))
disp(sum(v > 0))
```

```output
double 1 1
0
3 4
2
```

## Your turn

- `array_report(v)` — a struct describing `v`, with fields `n` (element count),
  `mn`, `mx`, `avg` and `kind` (the class name). Throws
  `array_report:empty` for an empty input.
- `trim_outliers(v, k)` — `v` without the elements more than `k` standard
  deviations from the mean. Elements exactly `k` away are **kept**.
- `interleave(a, b)` — `[a(1) b(1) a(2) b(2) ...]` as a row. Throws
  `interleave:sizeMismatch` when the lengths differ.
