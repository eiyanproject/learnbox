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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **logical array** (mask) | true/false per element, the same size as the input |
| **logical indexing** | using a mask as a subscript to select elements |
| **assign through a mask** | `v(mask) = x` changes only the selected elements |
| **element-wise logic** | `&`, `\|`: on arrays, both sides always evaluated |
| **short-circuit** | `&&`, `\|\|`: single values only; the second side is skipped if not needed |
| **guard** | a first test that protects the second, such as `~isempty(v) && v(1) > 0` |
| **implicit `all()`** | `if` on an array is true only if every element is non-zero |
| **position** | the index where something is |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `octave --no-gui --quiet --eval "..."` | runs one line of MATLAB code in Octave, with no window and no banner, as Run does |

### MATLAB names

| Name | What it does |
|---|---|
| `v > 0` | a mask |
| `v(v > 0)` | the elements where it is true |
| `sum(mask)` | counts the trues |
| `any(mask)`, `all(mask)` | at least one / every one |
| `v(v < 0) = 0` | replaces negatives |
| `v(v > 2 & v < 5)` | both conditions, element-wise |
| `find(mask)`, `find(mask, 1)` | positions / the first, or `[]` |
| `isempty(x)` | whether `x` has no elements |
| `~` | not |

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

## All of it, run

```matlab
v = [3 -1 4 -1 5];
disp(v > 0)
disp(v(v > 0))
disp(sum(v > 0))
w = v;
w(w < 0) = 0;
disp(w)
disp(v(v > 2 & v < 5))
if [1 0 1], disp('if [1 0 1]: true'), else, disp('if [1 0 1]: false'), end
if [], disp('if []: true'), else, disp('if []: false'), end
disp(find(v < 0))
disp(isempty(find(v > 10, 1)))
```

```output
1 0 1 0 1
3 4 5
3
3 0 4 0 5
3 4
if [1 0 1]: false
if []: false
2 4
1
```

## Your turn

- `count_above(v, t)` — how many elements exceed `t`
- `replace_negatives(v, r)` — every negative replaced by `r`
- `select_range(v, lo, hi)` — the elements in `[lo, hi]`, inclusive
- `first_above(v, t)` — the first position above `t`, or `[]`
