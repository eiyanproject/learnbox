---
title: Control flow
summary: if, switch, for and while - and the fact that a MATLAB for loop walks the columns of whatever you hand it.
order: 4
files: [grade.m, describe_sign.m, sum_until.m]
run: octave --no-gui --quiet --eval "disp(grade(85))"
hints:
  - "`if ... elseif ... else ... end`. There is no `elif`, and the `end` is required."
  - "Validate first: `if score < 0 || score > 100, error('grade:range', ...); end`."
  - "`switch` compares with isequal, so it works on char: `switch describe_sign_key, case 'positive', ...`."
  - "`sum_until` returns two things: the running total and how many elements went into it. Stop with `break` before exceeding the limit."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **control flow** | the order code runs in: `if`, `switch`, `for`, `while` |
| **`elseif`** | one word; another test |
| **ternary operator** | `a ? b : c`; MATLAB has none |
| **`switch`** | compares with `isequal`, so works on char arrays |
| **`otherwise`** | the default case |
| **fall-through** | a case running into the next; MATLAB has none |
| **`for` walks columns** | each loop value is one column of what it is given |
| **`break`** / **`continue`** | leave the loop / go to the next iteration |
| **preallocate** | make the full array before the loop |
| **vectorised** | the loop written as one array expression |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `octave --no-gui --quiet --eval "..."` | runs one line of MATLAB code in Octave, with no window and no banner, as Run does |

### MATLAB names

| Name | What it does |
|---|---|
| `if ... elseif ... else ... end` | branches |
| `switch name, case 'north', ..., case {'east','west'}, ..., otherwise, ..., end` | choose by value |
| `for i = 1:5 ... end` | a loop over 1 to 5 |
| `while total < limit ... end` | loops while a condition holds |
| `out = zeros(1, n)` | preallocates |
| `c{i}` | the contents of cell `i` |
| `error('grade:range', ...)` | throws with an identifier |
| `[total, used] = f(...)` | two outputs |

---

## if

```matlab
if score >= 90
  letter = 'A';
elseif score >= 80
  letter = 'B';
else
  letter = 'F';
end
```

`elseif` is one word. `end` closes the block and is not optional. There is no
ternary operator.

Remember from the last lesson: `if` on an **array** is an implicit `all()`, and
`if []` is false. Both are examined.

## switch

```matlab
switch name
  case 'north'
    ...
  case {'east', 'west'}      % a cell groups several values
    ...
  otherwise
    ...
end
```

`switch` compares with `isequal`, so unlike C it works on char arrays directly.
`otherwise` is the default. **There is no fall-through** — no `break` is needed
and none is allowed, which removes a whole category of C bug.

## for

```matlab
for i = 1:5
  ...
end
```

What is really happening: **`for` walks the columns** of whatever it is given.
`1:5` is a 1×5 row, so there are five columns and `i` is a scalar each time.
Hand it a matrix and `i` is a whole column:

```matlab
for col = [1 2; 3 4]     % col is [1;3], then [2;4]
```

And `for x = v'` on a column vector runs **once**, with the entire thing —
which is the bug this explains.

To iterate a cell array's contents you still index: `c{i}`.

## while, break, continue

```matlab
while total < limit
  ...
  if bad, break; end       % leave the loop
  if dull, continue; end   % next iteration
end
```

## Preallocate

```matlab
out = zeros(1, n);         % not out = []
for i = 1:n
  out(i) = ...;
end
```

Growing an array inside a loop reallocates and copies every time. And the real
lesson: most loops over an array want to be a vectorised expression instead.

## Columns, run

```matlab
for col = [1 2; 3 4]
  disp(col')
end

v = [1; 2; 3];
n = 0;
for x = v
  n = n + 1;
end
fprintf('%d iteration(s), x has %d elements\n', n, numel(x));

name = 'west';
switch name
  case 'north'
    disp('N')
  case {'east', 'west'}
    disp('E or W')
  otherwise
    disp('?')
end
```

```output
1 3
2 4
1 iteration(s), x has 3 elements
E or W
```

## Your turn

- `grade(score)` — `'A'` 90+, `'B'` 80+, `'C'` 70+, `'D'` 60+, `'F'` below;
  throws `grade:range` outside 0–100
- `describe_sign(n)` — `'negative'`, `'zero'` or `'positive'`, using `switch`
- `sum_until(v, limit)` — returns `[total, used]`, adding in order while the
  total would stay within `limit`
