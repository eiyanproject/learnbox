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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **address** | where a value lives in memory |
| **pointer** | a variable holding an address |
| **dereference** | follow a pointer to the value: `*p` |
| **pass by value** | a function gets a copy of each argument |
| **output parameter** | a pointer argument the function writes its answer through |
| **array** | several values of one type side by side |
| **decay** | an array name in an expression becomes a pointer to its first element |
| **element** | one item of an array |
| **scope** | where a name can be used |
| **pointer arithmetic** | `values + 2`: the address two elements further on |
| **`NULL`** | a pointer to nothing; dereferencing it is undefined behaviour |
| **use-after-free** | using memory after freeing it; often appears to work |
| **crash** | the program being stopped by the operating system |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `gcc -std=c17 -Wall ptr.c -o ptr && ./ptr` | builds and runs |

### C names

| Name | What it does |
|---|---|
| `int *p` | declares `p` as a pointer to `int` |
| `&x` | the address of `x` |
| `*p` | the thing `p` points at |
| `values[2]`, `*(values + 2)` | the same element |
| `void f(int values[])` | receives a pointer; the length is lost |
| `const int *values` | a pointer the function only reads through |
| `if (p != NULL)` | check before using a pointer you did not create |
| `printf("%zu", ...)` | prints a `size_t` |

### Errors

| Error | Means |
|---|---|
| `warning: 'sizeof' on array function parameter 'values' will return size of 'int *'` | `sizeof` inside a function measures the pointer |
| `Segmentation fault` | the program touched memory it may not, often a NULL dereference |

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

All three ideas, running:

```c
#include <stdio.h>

void broken(int x) { x = 99; }
void works(int *x) { *x = 99; }
size_t size_inside(int values[]) { return sizeof(values); }   /* gcc warns here */

int main(void) {
    int a = 1, b = 1;
    broken(a);
    works(&b);
    printf("a=%d b=%d\n", a, b);

    int values[5] = {10, 20, 30, 40, 50};
    printf("%d %d\n", values[2], *(values + 2));
    printf("outside=%zu inside=%zu\n", sizeof(values), size_inside(values));
    return 0;
}
```

```output
a=1 b=99
30 30
outside=20 inside=8
```

Five 4-byte ints outside; one 8-byte pointer inside.

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
