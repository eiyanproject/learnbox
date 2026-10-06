---
title: "Round 2: Moving mean"
summary: Smooth a noisy signal with a sliding window, and refuse a window that makes no sense.
order: 2
files: [moving_mean.m]
run: octave --no-gui --quiet --eval "disp(moving_mean([1 2 3 4], 2))"
challenge:
  minutes: 18
  xp: 200
  requires:
    xp: 450
---

The signal is too jumpy to plot. Smooth it.

## The task

Write `out = moving_mean(v, k)`.

Slide a window of `k` consecutive elements along the row vector `v`, one
step at a time, and return the mean of each position where the **whole**
window fits. The result is a row vector with `numel(v) - k + 1` elements.

```text
moving_mean([1 2 3 4], 2)         ->  [1.5 2.5 3.5]
moving_mean([2 4 6 8 10], 3)      ->  [4 6 8]
moving_mean([5 7], 2)             ->  6
moving_mean([3 1 4], 1)           ->  [3 1 4]
```

`k` must be a whole number from `1` to `numel(v)`. Otherwise raise an error
with the identifier `moving_mean:window`:

```matlab
error('moving_mean:window', 'the window must be a whole number from 1 to %d', numel(v));
```

A loop over the positions is fine. `cumsum` makes it possible without one.
