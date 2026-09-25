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

## Your turn

- `classify_all(v)` — a cell array the same size as `v`, each entry
  `'negative'`, `'zero'` or `'positive'`
- `safe_apply(f, v)` — `f` applied to each element, with `NaN` wherever `f`
  throws or gives something that is not a single number. It never throws.
- `checked_mean(v)` — the mean, after checking. Throws `checked_mean:empty`,
  `checked_mean:notNumeric` or `checked_mean:hasMissing`, in that order.
