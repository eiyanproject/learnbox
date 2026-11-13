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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **function file** | a `.m` file whose first line is `function`; the file name is the function name |
| **path** | the folders MATLAB looks in for functions |
| **local function** | a later function in the same file; visible only inside it |
| **script** | a file with no `function` line; runs in the caller's workspace |
| **workspace** | the set of variables a script or function can see |
| **multiple outputs** | `[lo, hi] = f(...)`: the caller decides how many to take |
| **`nargout`** / **`nargin`** | how many outputs were asked for / arguments passed |
| **default argument** | a value used when the caller gives none; set with `nargin` |
| **`arguments` block** | MATLAB R2019b's way to validate and default; not available here |
| **error identifier** | `component:mnemonic`: what code may depend on |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `octave --no-gui --quiet --eval "..."` | runs one line of MATLAB code in Octave, with no window and no banner, as Run does |

### MATLAB names

| Name | What it does |
|---|---|
| `function [mn, mx, avg] = summarise(v)` ... `end` | a function with three outputs |
| `min(v)`, `max(v)`, `mean(v)` | smallest, largest, average |
| `bounds(v)` | smallest and largest at once |
| `if nargin < 2, factor = 2; end` | a default argument |
| `isempty(v)` | whether `v` has no elements |
| `error('summarise:empty', 'no values to summarise')` | throws with an identifier |
| `try ... catch err ... end`, `err.identifier`, `err.message` | catch and inspect |
| `printf('%g %g %g\n', a, b, c)` | Octave's formatted print, like `fprintf` |
| `clear` | empties the workspace |

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

```matlab
try
  error('summarise:empty', 'no values to summarise');
catch err
  disp(err.identifier)
  disp(err.message)
end
```

```output
summarise:empty
no values to summarise
```

## Your turn

In `summarise.m`:

- `function [mn, mx, avg] = summarise(v)`, throwing `summarise:empty` for `[]`

In `scale.m`:

- `function out = scale(v, factor)`, where `factor` defaults to `2`
