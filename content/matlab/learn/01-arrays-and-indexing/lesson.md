---
title: Arrays and indexing
summary: One-based subscripts, end, the colon, and the difference between picking elements and deleting them.
order: 1
files: [take_first.m, take_last.m, every_other.m, swap_ends.m]
run: octave --no-gui --quiet --eval "disp(every_other(1:10))"
hints:
  - "`v(1:n)` takes the first n. Subscripts start at 1, not 0, and v(0) is an error."
  - "`end` inside a subscript means the last index, so the last n elements are `v(end-n+1:end)`."
  - "`v(1:2:end)` steps by two: start, step, stop. The step goes in the middle."
  - "`numel(v)` is the element count. Check it before indexing, or MATLAB throws its own index error."
---

Subscripts start at **1**. `v(1)` is the first element and `v(0)` is an error,
not a wrap-around. This trips up everyone arriving from C or Python, and it is
worth saying out loud once: the first element is number one.

## The colon

```matlab
v(2:4)        % elements 2, 3 and 4
v(1:2:end)    % every other one - start : step : stop
v(:)          % all of them, as a column
v(end)        % the last
v(end-1)      % the one before it
```

`end` is not a variable. Inside a subscript it means "the last index of this
dimension", which is why `v(end-n+1:end)` is the last `n` without you having to
know how long `v` is.

The step sits in the **middle**: `first:step:last`. `10:-1:1` counts down.

## Building them

```matlab
zeros(2, 3)        linspace(0, 1, 5)     % 5 points, endpoints included
ones(3, 1)         1:0.5:3               % a range with a step
```

`linspace(a, b, n)` and `a:step:b` both make ranges, and they answer different
questions: `linspace` guarantees the **count** and computes the step;
the colon guarantees the **step** and lets the count fall out. For endpoints
that must land exactly, `linspace` is the one.

## Growing, and why it is slow

```matlab
v(end+1) = 9;      % appends
```

Assigning past the end grows the array. It is also a reallocation and a copy
each time, so a loop that grows an array element by element is quadratic.
Preallocate with `zeros(1, n)` and assign into it.

## Deleting

```matlab
v(2) = [];         % removes the second element
```

Assigning the empty matrix **deletes**. It is not "set it to empty" — the array
gets shorter. That asymmetry with `v(2) = 0` is deliberate and is examined.

## Your turn

- `take_first(v, n)` — the first `n`, throwing `take_first:tooMany` if there
  are not that many
- `take_last(v, n)` — the last `n`
- `every_other(v)` — elements 1, 3, 5, …
- `swap_ends(v)` — the first and last exchanged
