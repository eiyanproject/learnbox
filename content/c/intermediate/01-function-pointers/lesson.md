---
title: Function pointers and callbacks
summary: Passing behaviour as a value, the declaration syntax nobody remembers, and the dispatch table that replaces a long switch.
order: 1
files: [cb.c, cb.h]
run: gcc -std=c17 -Wall cb.c -o cb && ./cb
hints:
  - "`int (*op)(int, int)` is a pointer to a function taking two ints and returning int. The parentheses around *op are what make it a function pointer rather than a function returning a pointer."
  - "`apply_all` walks an array applying the callback to each element in place; the callback takes an int and returns an int."
  - "`find_op` looks up a name in a table of {name, function} structs and returns the function pointer, or NULL."
  - "`qsort` needs a comparator of type `int (*)(const void *, const void *)`: cast both arguments back to `const int *` and dereference."
---

A function pointer holds the address of code rather than data. It is how C
passes behaviour around.

```c
int add(int a, int b) { return a + b; }

int (*op)(int, int) = add;   /* or &add - both work */
op(2, 3);                     /* or (*op)(2, 3) - both work too */
```

## The declaration

```c
int (*op)(int, int);    /* pointer to function returning int */
int *op(int, int);      /* function returning pointer to int - different thing */
```

The parentheses around `*op` are load-bearing. Without them, `*` binds to the
return type. This is why almost everyone writes a typedef:

```c
typedef int (*BinaryOp)(int, int);
BinaryOp op = add;
```

Read declarations outward from the name: *op* is a *pointer* to a *function*
taking two ints and *returning* int.

## Callbacks

The standard library already works this way:

```c
qsort(values, n, sizeof *values, compare);
```

`qsort` does not know what it is sorting. It knows the count, the element size,
and a function that orders two of them, all through `void *`. That is generic
programming in C — no templates, and no type checking either, which is the
trade.

A comparator returns negative, zero or positive:

```c
int compare_ints(const void *a, const void *b) {
    int x = *(const int *)a, y = *(const int *)b;
    return (x > y) - (x < y);     /* no overflow, unlike x - y */
}
```

`x - y` is the common shortcut and it is wrong: it overflows for large
magnitudes and gives the opposite answer.

## Dispatch tables

A table of name-to-function replaces a growing `switch`:

```c
static const struct { const char *name; BinaryOp fn; } OPS[] = {
    {"add", add}, {"sub", sub}, {"mul", mul},
};
```

Adding an operation becomes a table row rather than a new `case`, and the table
can be searched, counted and iterated — which a `switch` cannot.

## Your turn

In `cb.h` and `cb.c`:

- `typedef int (*BinaryOp)(int, int)` and `typedef int (*UnaryOp)(int)`
- `int add_op(int, int)`, `int sub_op(int, int)`, `int mul_op(int, int)`
- `BinaryOp find_op(const char *name)` — from a table, NULL if unknown
- `void apply_all(int *values, int n, UnaryOp f)` — in place
- `int reduce(const int *values, int n, int initial, BinaryOp f)`
- `void sort_ints(int *values, int n)` — using `qsort`
