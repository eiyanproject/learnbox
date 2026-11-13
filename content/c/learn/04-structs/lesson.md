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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **struct** | a type grouping several named values |
| **field** (member) | one value inside a struct |
| **copied on assignment** | `q = p` makes a full copy; so does passing a struct to a function |
| **pass by pointer** | passing the address, so nothing is copied |
| **precedence** | which operator binds tighter: `.` binds tighter than `*` |
| **`typedef`** | gives a type a new name, so `struct` can be left out |
| **padding** | unused bytes the compiler inserts so each field sits at an address its type likes |
| **alignment** | the address boundary a type prefers, such as 4 bytes for `int` |
| **layout** | where each field sits inside the struct |
| **unspecified** | the standard does not say what the padding bytes hold |
| **socket** | a network connection a program writes bytes to |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `gcc -std=c17 -Wall shape.c -o shape && ./shape` | builds and runs |

### C names

| Name | What it does |
|---|---|
| `struct Point { int x; int y; };` | defines a struct |
| `struct Point p = {3, 4};` | creates one with values |
| `p.x` | a field of a struct |
| `ptr->x` | a field through a pointer: the same as `(*ptr).x` |
| `const struct Rect *r` | read a struct without copying or changing it |
| `typedef struct { int x, y; } Point;` | a struct type named `Point` |
| `sizeof(struct Bad)` | the size including padding |
| `memcmp(a, b, n)` | compares bytes; never use it on structs |

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
fields largest-first usually shrinks it. Checking both claims - the copy and the
padding - on this machine:

```c
#include <stdio.h>

struct Point { int x; int y; };
struct Bad  { char a; int b; char c; };
struct Good { int b; char a; char c; };

int main(void) {
    struct Point p = {3, 4};
    struct Point q = p;          /* a copy, not a second name */
    q.x = 99;
    printf("p.x=%d q.x=%d\n", p.x, q.x);
    printf("Bad=%zu Good=%zu\n", sizeof(struct Bad), sizeof(struct Good));
    return 0;
}
```

```output
p.x=3 q.x=99
Bad=12 Good=8
```

Six bytes of data in both; `Bad` pads after `a` and after `c` to keep `b` on a
4-byte boundary. Two consequences that matter: never
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
