---
title: The preprocessor
summary: Textual substitution before the compiler sees anything, the macro pitfalls that follow from that, and when a macro is still the right answer.
order: 2
files: [pp.c, pp.h]
run: gcc -std=c17 -Wall pp.c -o pp && ./pp
hints:
  - "Wrap every macro parameter in parentheses AND the whole body too: `#define SQUARE(x) ((x) * (x))`. Both matter, for different reasons."
  - "`MAX` evaluates its arguments twice, which is why the test with a side effect exists - write it as a macro anyway and see."
  - "`safe_max` is the function version: it evaluates each argument once, because arguments to a function are evaluated before the call."
  - "`ARRAY_LEN` is `(sizeof(a) / sizeof((a)[0]))` and only works where the array's real type is visible - not on a pointer."
---

The preprocessor runs **before** the compiler and does textual substitution. It
has no idea about types, scopes or expressions — it pastes text.

Almost everything surprising about macros follows from that one fact.

## Parenthesise everything

```c
#define SQUARE(x) x * x
SQUARE(2 + 3)        /* becomes 2 + 3 * 2 + 3, which is 11 */
```

The fix is parentheses around each parameter **and** around the whole body:

```c
#define SQUARE(x) ((x) * (x))
```

The inner ones fix argument precedence, the outer ones fix how the result
combines with what surrounds it: `10 / SQUARE(2)` needs them.

## Double evaluation

```c
#define MAX(a, b) ((a) > (b) ? (a) : (b))
MAX(i++, 5)          /* i++ may happen twice */
```

Look at the expansion: both arguments are evaluated in the condition, and then
the **winner** is evaluated again as the result. So the larger argument happens
twice and the smaller happens once — and which is which depends on the values
at runtime, not on where you wrote them.

Correctly parenthesised and still wrong for any argument with a side effect —
or merely an expensive one, which is evaluated twice for no reason. A function
does not have this problem, because arguments are evaluated once, before the
call.

Prefer a `static inline` function whenever a macro is not required. The
compiler inlines it, you get type checking, and arguments are evaluated once.

## What macros are still for

- **Include guards** — nothing else can do this.
- **Conditional compilation** — `#ifdef DEBUG`, platform differences.
- **`ARRAY_LEN`** — needs the compile-time array type, so no function can do it.
- **`assert`** — needs `__FILE__` and `__LINE__` from the call site.
- **Constants that must be constant expressions** — array sizes, `case` labels.

`ARRAY_LEN` deserves its warning: it silently gives the wrong answer on a
pointer, which is what an array becomes when passed to a function.

## Useful predefined macros

`__FILE__`, `__LINE__`, `__func__` and `__DATE__`. The first two are why
assertion messages can point at the failing line, which is exactly what the
`ctest.h` this course uses does.

## Your turn

In `pp.h`, define macros:

- `SQUARE(x)`, safe for `SQUARE(2 + 3)` and `10 / SQUARE(2)`
- `MAX(a, b)` and `MIN(a, b)`
- `ARRAY_LEN(a)`
- `CLAMP(v, lo, hi)`

and in `pp.c` a function `int safe_max(int a, int b)` that evaluates each
argument exactly once.
