---
title: "Round 1: Clean readings"
summary: A sensor log with values out of range and gaps in it. Logical indexing, no loops needed.
order: 1
files: [in_range.m, valid_mean.m]
run: octave --no-gui --quiet --eval "disp(in_range([1 2 3 4], 2, 3))"
challenge:
  minutes: 12
  xp: 150
  requires:
    xp: 150
---

The temperature logger glitches. Some readings are impossible and some are
missing, and the daily summary is due.

## The task

Two functions, one file each.

`out = in_range(v, lo, hi)` returns the elements of the row vector `v` that
lie between `lo` and `hi`, **both ends included**, in their original order.
When nothing qualifies the result is an empty row vector.

```text
in_range([1 2 3 4], 2, 3)       ->  [2 3]
in_range([5 -1 7 5], 5, 7)      ->  [5 7 5]
in_range([1 2 3], 10, 20)       ->  zeros(1, 0)
```

`[avg, n] = valid_mean(v)` returns the mean of the elements of `v` that are
not `NaN`, and how many of them there are. With no valid elements at all,
`avg` is `0` and `n` is `0`.

```text
[avg, n] = valid_mean([4 NaN 8])    ->  avg = 6,  n = 2
[avg, n] = valid_mean([NaN NaN])    ->  avg = 0,  n = 0
```

Neither needs a loop: `isnan` and a logical mask do the work.
