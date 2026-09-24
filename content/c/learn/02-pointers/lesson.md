---
title: Pointers
summary: An address in a variable, what dereferencing costs you, and why a function that must change its argument takes a pointer.
order: 2
files: [ptr.c, ptr.h]
run: gcc -std=c17 -Wall ptr.c -o ptr && ./ptr
hints:
  - "`swap(int *a, int *b)` exchanges the values the pointers point AT, not the pointers themselves."
  - "`sum_and_count` writes two results through two out-parameters - check both pointers for NULL before writing, since the tests pass NULL deliberately."
  - "`find_index` returns the index or -1; iterate with a plain loop over `values[i]`, which is the same thing as `*(values + i)`."
  - "`increment_all` walks the array through a pointer: `for (int *p = values; p < values + n; p++) (*p)++;` is the idiomatic form."
---

A pointer holds an address. That is the whole idea; everything else follows
from it.

```c
int x = 42;
int *p = &x;     /* p holds the address of x */
*p = 99;         /* write through it: x is now 99 */
```

`&` takes an address, `*` follows one. In a declaration `int *p` means "p is a
pointer to int"; in an expression `*p` means "the thing p points at". Same
symbol, two jobs, which is most of why pointers read as confusing at first.

## Why they exist

C passes everything **by value**: a function gets a copy. So a function cannot
change its caller's variable — unless it is given the address:

```c
void broken(int x)  { x = 99; }      /* changes the copy */
void works(int *x)  { *x = 99; }     /* changes the caller's variable */

works(&value);
```

Every "output parameter" in C is this. So is every function that takes an array
— which brings us to the second reason.

## Arrays are not pointers, but they decay into them

```c
int values[5];
values[2]        /* the same as *(values + 2) */
```

An array **name** used in an expression becomes a pointer to its first element.
That is why `sizeof` works on an array in its own scope but not inside a
function that received it:

```c
void f(int values[]) {
    sizeof(values);   /* the size of a POINTER, not the array */
}
```

The length is lost at the boundary, which is why every C function taking an
array also takes a count. There is no other way to know.

## NULL, and the discipline around it

`NULL` is a pointer that points at nothing. Dereferencing it is undefined
behaviour — usually a crash, which is the good case.

Two habits worth forming immediately:

- **Check pointers you did not create.** Anything a caller handed you might be
  NULL, and an optional out-parameter usually is.
- **Set a pointer to NULL after freeing it.** A freed pointer still holds its
  old address, and using it is a use-after-free that often *appears* to work.

## Your turn

In `ptr.h` and `ptr.c`:

- `void swap(int *a, int *b)`
- `void sum_and_count(const int *values, int n, int *sum_out, int *count_out)` —
  either out-parameter may be NULL and must then be skipped
- `int find_index(const int *values, int n, int target)` — index or -1
- `void increment_all(int *values, int n)`
