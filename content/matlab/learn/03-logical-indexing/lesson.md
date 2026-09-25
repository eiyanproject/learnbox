---
title: Logical indexing
summary: A comparison gives an array of true and false, and an array of true and false can be a subscript. That pairing replaces most loops.
order: 3
files: [count_above.m, replace_negatives.m, select_range.m, first_above.m]
run: octave --no-gui --quiet --eval "disp(select_range(1:20, 5, 10))"
hints:
  - "`v > t` is not a number - it is a logical array the same size as v."
  - "`sum(mask)` counts the trues, because true adds as 1. No loop and no find."
  - "Use `&` and `|` between arrays. `&&` and `||` are for single true/false values only."
  - "`find(mask, 1)` gives the first index where the mask is true, and `[]` when it never is."
---

```matlab
v = [3 -1 4 -1 5];
v > 0
% 1  0  1  0  1      a LOGICAL array, not a list of positions
```

A comparison applies to every element and hands back a mask of the same size.
That mask can then be used as a subscript:

```matlab
v(v > 0)        % 3 4 5    - the elements where the mask is true
```

This is the single most MATLAB thing in MATLAB. Most loops a newcomer writes
are a mask and an assignment.

## Counting

```matlab
sum(v > 0)      % 3
```

`true` behaves as 1 in arithmetic, so summing a mask counts it. `any(mask)` and
`all(mask)` answer "at least one" and "every one" without counting at all.

## Assigning through a mask

```matlab
v(v < 0) = 0;           % every negative becomes zero
```

The left side selects, the right side supplies. A scalar on the right fills
every selected position; an array must have exactly as many elements as the
mask has trues.

## & against &&

| | |
|---|---|
| `&` `\|` | element-wise, on arrays, both sides always evaluated |
| `&&` `\|\|` | single values only, short-circuits |

```matlab
v(v > 2 & v < 5)        % correct - element-wise on arrays
v(v > 2 && v < 5)       % error, or worse, nonsense
```

`&&` requires each side to be one true or false. Use it in an `if`, where
short-circuiting protects the second test:

```matlab
if ~isempty(v) && v(1) > 0      % v(1) is only reached when v is non-empty
```

With `&` that guard would not work, because both sides are evaluated.

## if on an array

```matlab
if [1 0 1]     % false
```

`if` on an array is true only when **every** element is non-zero — it is an
implicit `all()`. An empty array is also false. This is a favourite exam
question and a real source of bugs; write `any(...)` or `all(...)` and say
which you meant.

## find

```matlab
find(mask)        % the positions where it is true
find(mask, 1)     % just the first, and [] if there are none
```

Prefer the mask itself when you want the elements. Use `find` when you want the
**position** — and take the `1` when you only need the first, so it stops
looking.

## Your turn

- `count_above(v, t)` — how many elements exceed `t`
- `replace_negatives(v, r)` — every negative replaced by `r`
- `select_range(v, lo, hi)` — the elements in `[lo, hi]`, inclusive
- `first_above(v, t)` — the first position above `t`, or `[]`
