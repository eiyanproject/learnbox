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
