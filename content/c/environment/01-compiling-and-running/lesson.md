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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **compiled ahead of time** | turned into machine code before it runs, with no runtime behind it |
| **binary** | the program file the computer runs |
| **compiler** | `gcc`: turns C into machine code |
| **preprocess** | the first stage: pastes in `#include`s and expands macros |
| **compile** | C to assembly, one file at a time |
| **assembly** | human-readable machine instructions |
| **assemble** | assembly to an object file |
| **object file** | `.o`: machine code for one source file, not yet joined |
| **link** | joining object files and libraries into one binary |
| **linker** | the program that links; reports undefined and duplicate symbols |
| **library** | already-compiled code a program can use |
| **symbol** | a named function or variable the linker connects |
| **macro** | a name the preprocessor replaces with text |
| **declaration** | the shape of a function: name, parameters, return type |
| **definition** | the body; exactly one across the whole program |
| **header** | a `.h` file of declarations shared between `.c` files |
| **include guard** | `#ifndef X_H / #define X_H / #endif`: makes a second paste of a header empty |
| **warning** | the compiler pointing out likely mistakes it still allows |
| **C17** | the 2017 version of the C standard |
| **debug information** | data `-g` adds so a debugger can show your source |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `gcc calc.c -o calc` | compiles and links `calc.c` into the program `calc` |
| `-std=c17` | use the C17 standard |
| `-Wall -Wextra` | turn on most warnings |
| `-g` | include debug information |
| `./calc` | runs the program |

### C names

| Name | What it does |
|---|---|
| `#include "calc.h"` | pastes in a header |
| `#ifndef`, `#define`, `#endif` | the include guard |
| `int c_max(int a, int b);` | a declaration (ends with `;`) |
| `const char *` | a pointer to text the function will not change |
| `int main(void)` | where a program starts; the tests bring their own here |

### Errors

| Error | Means |
|---|---|
| `undefined reference to 'foo'` | the linker found a declaration but no definition |
| `implicit declaration of function 'foo'` | the compiler never saw it declared, usually a missing `#include` |
| `multiple definition of 'foo'` | two definitions; the linker needs exactly one |
| `fatal error: x.h: No such file or directory` | a missing header |

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
