---
title: Scripts, functions and the workspace
summary: One function per file, why that rule exists, and how nargin and multiple returns let one function answer several questions.
order: 2
files: [summarise.m, scale.m]
run: octave --no-gui --quiet --eval "[a,b,c] = summarise([3 1 4]); printf('%g %g %g\n', a, b, c)"
hints:
  - "`function [mn, mx, avg] = summarise(v)` declares three outputs; assign all three in the body."
  - "An empty input has no minimum, so `summarise([])` must throw: `error('summarise:empty', 'no values to summarise')`."
  - "`scale` uses `nargin` for its default: `if nargin < 2, factor = 2; end`."
  - "`isempty(v)` is the check, not `length(v) == 0` - it reads better and works for every shape."
---

## A file is a function

```matlab
% saved as summarise.m
function [mn, mx, avg] = summarise(v)
  mn = min(v);
  mx = max(v);
  avg = mean(v);
end
```

The **file name is the function name**, and that is how MATLAB finds it — there
is no import and no declaration. `summarise.m` on the path gives you
`summarise`. Rename the file and you rename the function.

A file may hold more functions after the first. Those are **local** functions:
visible to each other and to the first one, invisible from anywhere else. That
is the unit of privacy in MATLAB.

## Scripts are different

A script is a file with no `function` line. It runs in the **caller's
workspace**, so it can see and change your variables. That makes scripts
convenient and makes them the usual source of a bug that disappears when you
`clear`.

Functions get a fresh workspace each call and can only see what was passed in.
Prefer a function.

## Multiple outputs

```matlab
[lo, hi] = bounds(v);
lo = bounds(v);          % the extra outputs are simply not computed
```

The caller decides how many to take, and `nargout` inside the function tells
you how many were asked for. That is how `size` returns `[r, c]` or a single
`[r c]` vector depending on how you call it.

## nargin and defaults

MATLAB has no default-argument syntax. `nargin` is the count of arguments
actually passed:

```matlab
if nargin < 2
  factor = 2;
end
```

The modern alternative is an `arguments` block, which also validates. It is
MATLAB R2019b and later, and is not available here.

## Errors

```matlab
error('summarise:empty', 'no values to summarise');
```

The first part is the **identifier**, `component:mnemonic`. It is the piece
code is allowed to depend on — `catch err` then gives you `err.identifier`,
which is stable, and `err.message`, which is for a person and may be reworded.

## Your turn

In `summarise.m`:

- `function [mn, mx, avg] = summarise(v)`, throwing `summarise:empty` for `[]`

In `scale.m`:

- `function out = scale(v, factor)`, where `factor` defaults to `2`
