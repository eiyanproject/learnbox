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

## Your turn

- `array_report(v)` — a struct describing `v`, with fields `n` (element count),
  `mn`, `mx`, `avg` and `kind` (the class name). Throws
  `array_report:empty` for an empty input.
- `trim_outliers(v, k)` — `v` without the elements more than `k` standard
  deviations from the mean. Elements exactly `k` away are **kept**.
- `interleave(a, b)` — `[a(1) b(1) a(2) b(2) ...]` as a row. Throws
  `interleave:sizeMismatch` when the lengths differ.
