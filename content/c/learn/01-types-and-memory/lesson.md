---
title: Types, sizes and integer behaviour
summary: What a C type really is - a size and a way of reading bytes - plus overflow, truncation and the promotions that happen before you notice.
order: 1
files: [nums.c, nums.h]
run: gcc -std=c17 -Wall nums.c -o nums && ./nums
hints:
  - "`type_size` returns sizeof for a name: compare with strcmp and return (int)sizeof(int) and friends."
  - "`safe_add` must detect overflow BEFORE it happens - signed overflow is undefined behaviour, so you cannot add and then check the sign."
  - "For `safe_add`: if b > 0 and a > INT_MAX - b it would overflow; if b < 0 and a < INT_MIN - b it would underflow."
  - "`truncate_to_char` casts an int to signed char and back - values above 127 wrap, which is the point."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **type** | how many bytes, and how to interpret them |
| **byte** | 8 bits; `char` is exactly one |
| **runtime type** | type information kept while running; C has none |
| **signed** / **unsigned** | can be negative / only zero and up |
| **`size_t`** | the unsigned type `sizeof` and `strlen` return |
| **fixed-width integers** | `int32_t`, `uint64_t`, `int8_t`: exactly that many bits |
| **overflow** | a result too big for its type |
| **undefined behaviour** | the standard says nothing about what happens; the compiler may assume it never does |
| **wrap** | unsigned overflow going round to 0; defined |
| **optimise** | the compiler rewriting code to run faster |
| **truncation** | only the low bits survive a conversion to a narrower type |
| **integer division** | `7 / 2` is 3; the fraction is dropped before any assignment |
| **promotion** | anything narrower than `int` becomes `int` before arithmetic |
| **x86-64** | the 64-bit PC processor family these lessons run on |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `gcc -std=c17 -Wall nums.c -o nums && ./nums` | builds and runs |

### C names

| Name | What it does |
|---|---|
| `sizeof(int)`, `sizeof x` | the size in bytes |
| `char`, `int`, `long`, `double` | basic types |
| `<stdint.h>` | the fixed-width integer types |
| `<limits.h>` | `INT_MAX`, `INT_MIN`, `CHAR_BIT` and other limits |
| `<string.h>`, `strlen(s)` | string functions; a string's length |
| `printf("%d %zu %.1f\n", ...)` | prints an `int`, a `size_t`, a `double` with one decimal |
| `if (b > 0 && a > INT_MAX - b)` | an overflow check written before the addition |
| `int *out` | an output parameter: the function writes the answer through it |
| `signed char` | a one-byte signed type |
| `return 0;` | `main` reports success |

---

A C type is two pieces of information: how many bytes, and how to interpret
them. That is all. There is no runtime type, no checking, and nothing stopping
you reading the same bytes as something else.

## Sizes are not guaranteed

```c
sizeof(char)    /* exactly 1, by definition */
sizeof(int)     /* 4 on almost everything today, but the standard says >= 2 */
sizeof(long)    /* 8 on Linux, 4 on Windows */
```

`sizeof` yields a `size_t`, which is unsigned. That matters more than it looks:

```c
if (strlen(s) - 1 >= 0)    /* always true: the result is unsigned */
```

When a length is zero, `0 - 1` becomes a huge positive number rather than -1.
This is one of the most common C bugs and the compiler will not warn by
default.

Use `<stdint.h>` when the width matters: `int32_t`, `uint64_t`, `int8_t`. The
names say exactly what you get.

## Overflow is undefined, not wrapping

For **signed** integers, overflow is undefined behaviour. Not "wraps to
negative" — undefined, meaning the compiler may assume it never happens and
optimise on that basis:

```c
if (a + 1 < a)    /* a compiler may delete this: it "cannot" be true */
```

For **unsigned** integers, wrapping is defined and does what you expect. That
asymmetry is why overflow checks must be written *before* the operation:

```c
if (b > 0 && a > INT_MAX - b) { /* would overflow */ }
```

`<limits.h>` has `INT_MAX`, `INT_MIN`, `CHAR_BIT` and the rest.

## Conversions happen silently

```c
int  big = 300;
char c = big;        /* truncated: only the low 8 bits survive */
double d = 7 / 2;    /* 3.0 - the division was integer before the assignment */
```

And before nearly any arithmetic, anything narrower than `int` is **promoted**
to `int`. A `char + char` is an `int` expression, which is why `printf("%d",
c)` works and why overflow in `char` arithmetic is often not where you expect.

## Seeing it

All of the above in one program, and what it prints on x86-64 Linux, where
these lessons run:

```c
#include <stdio.h>
#include <string.h>

int main(void) {
    printf("char=%zu int=%zu long=%zu\n", sizeof(char), sizeof(int), sizeof(long));

    int big = 300;
    char c = big;            /* 300 - 256: only the low 8 bits survive */
    double d = 7 / 2;        /* integer division first */
    printf("c=%d d=%.1f\n", c, d);

    size_t len = strlen("");
    printf("len - 1 = %zu\n", len - 1);    /* unsigned: wraps, never -1 */
    return 0;
}
```

```output
char=1 int=4 long=8
c=44 d=3.0
len - 1 = 18446744073709551615
```

## Your turn

In `nums.h` and `nums.c`:

- `int type_size(const char *name)` — `sizeof` for `"char"`, `"int"`,
  `"long"`, `"double"`; `-1` for anything else
- `int safe_add(int a, int b, int *out)` — 1 and the sum through `out`, or 0
  and `out` untouched when it would overflow
- `unsigned wrap_add(unsigned a, unsigned b)` — unsigned addition, which
  wraps by definition
- `int truncate_to_char(int value)` — the value as a `signed char`, widened
  back
