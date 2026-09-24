---
title: The compiler, the linker and the binary
summary: What gcc actually does to a .c file, why a declaration and a definition are different things, and what a header is for.
order: 1
files: [calc.c, calc.h]
run: gcc -std=c17 -Wall calc.c -o calc && ./calc
hints:
  - "`calc.h` holds the DECLARATIONS - just the signatures, ending in a semicolon. `calc.c` holds the DEFINITIONS - the bodies."
  - "Include guards stop a header being pasted in twice: `#ifndef CALC_H` / `#define CALC_H` at the top and `#endif` at the bottom."
  - "`c_max` returns the larger of two ints; `clamp` pins a value between lo and hi; `is_even` handles negatives correctly."
  - "The test file provides its own main, so calc.c must NOT define one - a second main is a linker error."
---

C is compiled ahead of time into a binary with no runtime behind it. Four
stages happen when you type `gcc calc.c -o calc`:

| Stage | Does | Fails with |
|---|---|---|
| Preprocess | pastes in `#include`s, expands macros | missing header |
| Compile | C to assembly, one file at a time | syntax and type errors |
| Assemble | assembly to an object file | rarely |
| Link | joins objects and libraries | undefined reference, duplicate symbol |

Knowing which stage failed tells you where to look. **"undefined reference to
`foo`"** is the linker: the compiler was happy because it saw a declaration,
and no definition ever turned up. **"implicit declaration of function"** is the
compiler: you called something it has never heard of, usually a missing
`#include`.

## Declaration against definition

```c
int add(int a, int b);            /* declaration: the shape */
int add(int a, int b) { ... }     /* definition: the body */
```

The compiler only needs the declaration to compile a call. The linker needs
exactly one definition across the whole program. That split is why C has
headers at all, and why you can compile a file that references code you have
not written yet.

## Headers

A header holds declarations so several `.c` files can agree about the same
function without copying it:

```c
#ifndef CALC_H
#define CALC_H

int c_max(int a, int b);

#endif
```

The `#ifndef` is an **include guard**. `#include` is a literal paste, so a
header reached twice — directly and through another header — would declare
everything twice. The guard makes the second paste empty.

## Warnings are the type system

C will compile almost anything. `-Wall -Wextra` is where it tells you about the
mistakes it would otherwise let through, and treating those warnings as errors
is the single cheapest improvement to a C codebase.

```bash
gcc -std=c17 -Wall -Wextra -g calc.c -o calc
```

## Your turn

In `calc.h` and `calc.c`:

- `int c_max(int a, int b)` — the larger
- `int clamp(int value, int lo, int hi)` — pinned to the range
- `int is_even(int n)` — 1 or 0, correct for negatives
- `const char *sign_of(int n)` — `"negative"`, `"zero"` or `"positive"`

Declare them in the header, define them in the .c, and do not write a `main` —
the tests bring their own.
