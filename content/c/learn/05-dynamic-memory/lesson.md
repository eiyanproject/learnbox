---
title: malloc, free and who owns what
summary: Memory that outlives its scope, the four ways it goes wrong, and writing the ownership rule down because the compiler will not.
order: 5
files: [dyn.c, dyn.h]
run: gcc -std=c17 -Wall dyn.c -o dyn && ./dyn
hints:
  - "`make_range` allocates n ints and fills them 0..n-1. Return NULL for n <= 0, and check that malloc itself did not return NULL."
  - "`dup_string` needs strlen(s) + 1 bytes - the terminator is the byte everyone forgets."
  - "`grow_array` uses realloc, which may MOVE the block: assign its result rather than assuming the old pointer is still good."
  - "If realloc fails it returns NULL and the ORIGINAL block is still valid, so never write `p = realloc(p, ...)` without a temporary - you would leak the original."
---

Local variables die at the end of their scope. Anything that must outlive it
goes on the heap, and the heap has no owner unless you decide who it is.

```c
int *values = malloc(n * sizeof *values);
if (values == NULL) { /* out of memory */ }
...
free(values);
```

`sizeof *values` rather than `sizeof(int)` means the line stays correct if the
type changes. It is a small habit that removes a whole class of mistake.

**`malloc` does not initialise.** The bytes are whatever was there. `calloc(n,
size)` zeroes them and checks the multiplication for overflow, which `malloc(n
* size)` does not.

## The four ways it goes wrong

| | |
|---|---|
| **Leak** | never freed — the program grows until it dies |
| **Double free** | freed twice — heap corruption, often much later |
| **Use after free** | used after freeing — often *appears* to work |
| **Buffer overflow** | wrote past the end — corrupts the block header |

Only the first is merely wasteful. The other three corrupt state and typically
crash somewhere unrelated, which is why they are so expensive to find.

`free(NULL)` is explicitly safe and does nothing, so guards before it are
unnecessary. Setting the pointer to `NULL` after freeing is worth doing: it
turns a use-after-free into an immediate crash instead of a mystery.

## realloc moves

```c
int *bigger = realloc(values, new_count * sizeof *values);
if (bigger == NULL) { free(values); return NULL; }   /* original still valid */
values = bigger;
```

`realloc` may return a **different** address, having copied your data. Any
other pointer into the old block is now dangling. And on failure it returns
NULL while leaving the original allocated — so `p = realloc(p, n)` leaks the
original whenever it fails.

## Write the ownership rule down

C has no way to express "the caller must free this". A comment is the only
mechanism there is:

```c
/* Returns a newly allocated array; the caller frees it. */
int *make_range(int n);
```

Every allocating function needs that sentence, and every codebase that skips it
leaks.

## Your turn

In `dyn.h` and `dyn.c` — each returning memory the caller frees:

- `int *make_range(int n)` — 0..n-1, or NULL for n <= 0
- `char *dup_string(const char *s)` — a copy, or NULL
- `int *grow_array(int *values, int old_n, int new_n)` — realloc'd, new slots
  zeroed, NULL on failure without leaking
- `int sum_and_free(int *values, int n)` — sums, frees, returns the total
