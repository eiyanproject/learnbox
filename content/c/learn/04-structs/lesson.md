---
title: Structs and how they are laid out
summary: Grouping values into one type, the difference between . and ->, and the padding the compiler inserts without telling you.
order: 4
files: [shape.c, shape.h]
run: gcc -std=c17 -Wall shape.c -o shape && ./shape
hints:
  - "`struct Point` and `struct Rect` go in the HEADER - the tests construct them directly, so they need the full definition, not just a name."
  - "A function taking a struct by value copies the whole thing; taking `const struct Rect *` copies only an address. Use the pointer form for rect_area."
  - "`->` is shorthand: `r->w` means `(*r).w`. Use it whenever you have a pointer to a struct."
  - "`move_point` changes the caller's point, so it takes `struct Point *` and writes through it."
---

A struct groups values into one type:

```c
struct Point {
    int x;
    int y;
};

struct Point p = {3, 4};
p.x = 5;
```

Unlike an array, a struct **is** copied on assignment and when passed to a
function. That is convenient for small ones and expensive for large ones, which
is why anything beyond a few fields is usually passed by pointer.

## Dot and arrow

```c
struct Point p;
struct Point *ptr = &p;

p.x       /* a struct: use dot */
ptr->x    /* a pointer to one: use arrow, which is (*ptr).x */
```

`->` exists only because `(*ptr).x` is tedious and `*ptr.x` parses wrongly —
`.` binds tighter than `*`, so it would mean `*(ptr.x)`.

## const pointers to structs

```c
int rect_area(const struct Rect *r);
```

Takes an address, so nothing is copied, and promises not to modify. This is the
default shape for a function that reads a struct, and it is worth writing even
when the struct is small — it documents intent.

## typedef

```c
typedef struct { int x, y; } Point;
Point p;                    /* no "struct" keyword needed */
```

Common, and slightly controversial: it hides that the type is a struct. The
Linux kernel forbids it; plenty of other codebases require it. Both work.

## Padding

The compiler inserts padding so each field sits at an address its type likes:

```c
struct Bad  { char a; int b; char c; };   /* often 12 bytes */
struct Good { int b; char a; char c; };   /* often 8 */
```

`sizeof` a struct is therefore **not** the sum of its fields, and ordering
fields largest-first usually shrinks it. Two consequences that matter: never
compare structs with `memcmp` (the padding bytes are unspecified), and never
assume a struct's layout when writing it to a file or a socket.

## Your turn

In `shape.h` define `struct Point { int x; int y; }` and
`struct Rect { struct Point origin; int w; int h; }`, and declare:

- `struct Point point_of(int x, int y)`
- `void move_point(struct Point *p, int dx, int dy)`
- `int rect_area(const struct Rect *r)`
- `int rect_contains(const struct Rect *r, struct Point p)` — 1 or 0, with the
  origin inclusive and the far edge exclusive
- `struct Rect rect_grow(struct Rect r, int by)` — a new, larger rect with the
  same origin
