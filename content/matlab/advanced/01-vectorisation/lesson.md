---
title: Vectorisation
summary: Saying it to the whole array at once - and the built-ins that already are the loop you were about to write.
order: 1
files: [running_total.m, normalise.m, pairwise_diff.m, count_runs.m]
run: octave --no-gui --quiet --eval "disp(count_runs([1 1 2 2 2 3]))"
hints:
  - "`cumsum(v)` is the running total, already written."
  - "`normalise` maps to [0, 1] with `(v - min(v)) / (max(v) - min(v))`. A constant vector makes that 0/0 - decide what it should give."
  - "`diff(v)` gives the gaps between neighbours, one element shorter than v."
  - "A run ends wherever `diff(v) ~= 0`, so the number of runs is that count plus one - with an empty vector as its own case."
---

```matlab
for i = 1:numel(v)
  out(i) = v(i) * 2;
end

out = v * 2;
```

The second is not a shorter spelling of the first. MATLAB's array operations
run in compiled code over the whole block, and the loop runs the interpreter
once per element. The gap is large on real data.

It is also clearer, which matters more often than the speed does.

## The loop is probably already a function

| Instead of a loop that... | write |
|---|---|
| accumulates a running total | `cumsum(v)` |
| takes differences of neighbours | `diff(v)` |
| multiplies everything together | `cumprod(v)` |
| counts matches | `sum(mask)` |
| finds where | `find(mask)` |
| applies a condition | `v(mask)` |
| finds the extreme and its place | `[m, i] = max(v)` |

`diff` is one shorter than its input. That is not an off-by-one: there are
`n-1` gaps between `n` points.

## When you must loop

Preallocate.

```matlab
out = zeros(1, n);        % not out = []
for i = 1:n
  out(i) = expensive(i);
end
```

Growing an array reallocates and copies every iteration, which turns a linear
loop into a quadratic one. MATLAB's editor warns about this, and the warning is
worth obeying.

Genuine reasons to keep a loop: each step depends on the last in a way `cumsum`
cannot express; the body has side effects; or the vectorised version would
build an intermediate too large for memory. That last one is real — a fully
vectorised solution that allocates a 10,000×10,000 temporary is worse than the
loop.

## Measuring

```matlab
tic; slow_way(v); toc
```

Measure before rewriting. The loop you are about to spend an hour vectorising
may be running once on twelve elements.

## Your turn

- `running_total(v)` — the cumulative sum
- `normalise(v)` — scaled to `[0, 1]`; a constant vector gives all zeros
- `pairwise_diff(v)` — the gaps between neighbours
- `count_runs(v)` — how many runs of equal consecutive values; `0` for empty
