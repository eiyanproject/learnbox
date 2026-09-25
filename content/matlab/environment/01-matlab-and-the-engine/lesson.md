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

Two smaller ones: `numel` is not overloaded on the shim types, so use
`length`, `size`, `strlength` or `height`; and there is no Live Editor, no
Simulink and no toolboxes.

## Your turn

In `describe.m`:

- `function s = describe(v)` — a char row of the class and size, like
  `'double 2x3'` or `'char 1x5'`

In `is_text.m`:

- `function t = is_text(v)` — true for a char array **or** a string
