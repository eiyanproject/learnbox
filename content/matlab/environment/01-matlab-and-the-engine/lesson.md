---
title: MATLAB, and the engine under these lessons
summary: Everything is an array, every value has a class, and what runs your code here is Octave - which matters in exactly one place.
order: 1
files: [describe.m, is_text.m]
run: octave --no-gui --quiet --eval "disp(describe(magic(3)))"
hints:
  - "`class(v)` gives the type name as a char row: 'double', 'char', 'cell', 'logical'."
  - "`size(v)` returns [rows, cols]. `size(v, 1)` and `size(v, 2)` pick one."
  - "Build the answer with sprintf: `sprintf('%s %dx%d', class(v), size(v,1), size(v,2))`."
  - "`is_text` is true for a char array or a string. `ischar` covers the first; `isa(v, 'string')` covers the second."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **MATLAB** | a language and environment for numerical work |
| **array** | everything is one: a scalar is a 1-by-1 array |
| **scalar**, **vector**, **matrix** | one value / one row or column / rows and columns |
| **double** | the default numeric type |
| **char** | text as characters |
| **logical** | true or false |
| **cell** | a container that can hold mixed types |
| **saturate** | `int8(200)` stops at 127 instead of wrapping |
| **workspace** | the variables that persist between commands |
| **GNU Octave** | the open implementation of the language these lessons run on |
| **shim library** | this course's versions of `string`, `table`, `datetime` and `categorical` for Octave |
| **string literal** | `"Ada"`: a string in MATLAB, a char array in Octave; write `string('Ada')` |
| **headless** | running with no window |
| **Live Editor**, **Simulink**, **toolboxes** | MATLAB extras Octave does not have |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `octave --no-gui --quiet --eval "..."` | runs one line of MATLAB code in Octave, with no window and no banner, as Run does |

### MATLAB names

| Name | What it does |
|---|---|
| `size(x)`, `class(x)` | the dimensions / the type |
| `int8(200)` | an 8-bit integer, saturating |
| `disp(x)`, `fprintf(...)` | print |
| `who`, `whos`, `clear` | list, list with details, empty the workspace |
| `ischar(v)`, `isstring(v)` | whether `v` is a char array / a string |
| `sprintf('%s %dx%d', ...)` | builds text such as `'double 2x3'` |
| `magic(3)` | a 3-by-3 test matrix |
| `length`, `height`, `strlength` | use these instead of `numel` on the shim types |

---

## Everything is an array

```matlab
x = 5;
```

That is not a number. It is a 1×1 matrix of doubles, and `size(x)` says so.
A scalar, a vector and a matrix are the same kind of thing at different sizes,
which is why so much of MATLAB works on all three without you asking.

```matlab
class(5)        % 'double'  - the default numeric type
class('hi')     % 'char'    - text as characters
class(true)     % 'logical'
class({1, 'a'}) % 'cell'    - a container that can hold mixed types
```

Numbers are **double** unless you say otherwise. `int8(200)` saturates to 127
rather than wrapping, which is a real difference from C and a favourite exam
question.

All of that, printed:

```matlab
x = 5;
disp(size(x))
disp(class(5)); disp(class('hi')); disp(class(true)); disp(class({1, 'a'}))
disp(int8(200))
disp(int8(-200))
```

```output
1 1
double
char
logical
cell
127
-128
```

Examples here print with `disp` and `fprintf`, which show the same text in MATLAB and in Octave. Typing a bare expression, like
`class(5)` with no semicolon, also shows its value, but the two lay it out
slightly differently.

## The workspace

Variables live in a workspace that persists between commands. `who` lists it,
`clear` empties it, and `whos` adds class and size. A stale variable from an
earlier experiment is the single most common reason a script "works" once and
never again — which is why a graded check here always runs in a fresh process.

## The engine

MATLAB is licensed per seat and has no headless install, so these lessons run
on **GNU Octave**, which implements the same core language. Arrays, indexing,
operators, control flow, functions, `classdef` — all the same.

Four types Octave lacks are supplied by this course as a shim library, and they
behave like the MATLAB ones for everything the lessons do: **string**,
**table**, **datetime** and **categorical**. You will use them exactly as you
would in MATLAB.

**One difference cannot be papered over.** MATLAB has a string *literal*:

```matlab
name = "Ada";     % in MATLAB this is a string
name = 'Ada';     % in MATLAB this is a char array
```

In Octave both of those are char arrays. So when a lesson wants a string, it
says so:

```matlab
name = string('Ada');
```

Everything else about strings works normally. Where it matters, the lesson will
remind you.

Three smaller ones: `numel` is not overloaded on the shim types, so use
`length`, `size`, `strlength` or `height`; reaching through a table column
into a cell in one step, `t.Name{:}`, gives only the **first** value, so take
the column into a variable first (`names = t.Name; names{:}`); and there is no
Live Editor, no Simulink and no toolboxes.

## Your turn

In `describe.m`:

- `function s = describe(v)` — a char row of the class and size, like
  `'double 2x3'` or `'char 1x5'`

In `is_text.m`:

- `function t = is_text(v)` — true for a char array **or** a string
