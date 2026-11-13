---
title: "Paper 4: programming and debugging"
summary: Control flow, function handles, and failing in a way the caller can act on.
order: 4
files: [classify_all.m, safe_apply.m, checked_mean.m]
run: octave --no-gui --quiet --eval "disp(classify_all([-1 0 1]))"
hints:
  - "Preallocate the cell: `out = cell(size(v));` and then fill it."
  - "`safe_apply` needs a try/catch inside the loop, so one bad element does not stop the rest."
  - "`nan(size(v))` makes the right-shaped array of NaN to start from."
  - "Check in order - empty, then type, then content - and throw a different identifier for each."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **control flow** | `if`, `for`, `while`, `switch` |
| **implicit `all()`** | `if` on an array is true only if every element is |
| **`if []`** | false |
| **anonymous function** | `@() n`: captures variables by value when created |
| **function handle** | a function stored in a variable |
| **normal outcome** vs **bug** | report it (flag, `NaN`) / throw |
| **swallow** | a bare `catch` that hides every error |
| **preallocate** | make the full array before a loop fills it |
| **cell array** | `{ }`: holds text of different lengths |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `octave --no-gui --quiet --eval "..."` | runs one line of MATLAB code in Octave, with no window and no banner, as Run does |

### MATLAB names

| Name | What it does |
|---|---|
| `if ... elseif ... else ... end` | branches |
| `for i = 1:numel(v) ... end` | a loop |
| `cell(size(v))` | an empty cell array the same size as `v` |
| `f = @(x) x^2;` | an anonymous function |
| `try ... catch ... end` | catches errors |
| `isscalar(x)`, `isnumeric(x)` | whether `x` is one value / a number |
| `NaN(size(v))` | an array of `NaN` |
| `any(isnan(v))` | whether any value is missing |
| `error('checked_mean:empty', ...)` | throws with an identifier |

---

The last paper covers **programming and debugging**: control flow, functions
and handles, and errors.

Worth having straight:

- `if` on an array is an implicit `all()`, and `if []` is false
- an anonymous function captures by value when it is created
- an error identifier is what a caller may depend on; the message is not
- a bare `catch` that swallows everything turns a crash into wrong output
- preallocate before a loop that fills an array

The question underneath most of this domain is the same one: **is this a
normal outcome of correct code?**

Text where a number was expected, a lookup that misses, a file that might not
be there — all normal. Report them: a status flag, an extra output, a `NaN` in
the right place. A negative length, a missing required argument, an index past
the end — those mean the caller has a bug, and an exception is right because it
cannot be ignored.

Getting this backwards in either direction hurts. Throwing for ordinary input
makes a function that nobody can call without a `try`; returning a quiet `-1`
for a real bug makes one that fails somewhere else, later, for reasons nobody
can trace.

The first two rules, run:

```matlab
if [1 0 1], disp('true'), else, disp('false'), end
if [], disp('true'), else, disp('false'), end
n = 1;
f = @() n;
n = 2;
disp(f())
```

```output
false
false
1
```

## Your turn

- `classify_all(v)` — a cell array the same size as `v`, each entry
  `'negative'`, `'zero'` or `'positive'`
- `safe_apply(f, v)` — `f` applied to each element, with `NaN` wherever `f`
  throws or gives something that is not a single number. It never throws.
- `checked_mean(v)` — the mean, after checking. Throws `checked_mean:empty`,
  `checked_mean:notNumeric` or `checked_mean:hasMissing`, in that order.
