---
title: "Round 3: Runs"
summary: Squeeze a signal into its runs of repeated values and expand it back, with diff and find instead of a loop.
order: 3
files: [run_lengths.m, expand_runs.m]
run: octave --no-gui --quiet --eval "[v, c] = run_lengths([5 5 5 2 2 7])"
challenge:
  minutes: 20
  xp: 250
  requires:
    xp: 600
---

The valve sensor reports the same value thousands of times in a row. Store
each run once.

## The task

Two functions, one file each.

### `[values, counts] = run_lengths(v)`

`v` is a row vector. A **run** is a stretch of equal neighbouring elements.
Return the value of each run and how long it is, as two row vectors of the
same length.

```text
run_lengths([5 5 5 2 2 7])    ->  values = [5 2 7],  counts = [3 2 1]
run_lengths([4 4 4 4])        ->  values = 4,        counts = 4
run_lengths([1 2 1])          ->  values = [1 2 1],  counts = [1 1 1]
run_lengths([])               ->  values = zeros(1, 0),  counts = zeros(1, 0)
```

A value that comes back later starts a new run: `[1 2 1]` is three runs.

### `v = expand_runs(values, counts)`

The reverse: a row vector with each value repeated its count of times.
`expand_runs([5 2 7], [3 2 1])` is `[5 5 5 2 2 7]`. A count of `0` leaves
that value out. Two empty inputs give `zeros(1, 0)`.

If `values` and `counts` do not have the same number of elements, raise an
error with the identifier `expand_runs:size`.

For any row vector `v`, expanding its runs gives `v` back.

`diff(v) ~= 0` marks where one run ends and the next begins, and `find`
turns those marks into positions; `repelem` does the expanding. A loop
passes too.
