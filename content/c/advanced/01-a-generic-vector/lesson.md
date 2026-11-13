---
title: A generic container with void*
summary: How C does generics - an element size and raw bytes - and the growth strategy that makes append amortised constant.
order: 1
files: [vec.c, vec.h]
run: gcc -std=c17 -Wall vec.c -o vec && ./vec
hints:
  - "Store `elem_size` in the struct. Element i lives at `(char *)data + i * elem_size` - cast to char* because arithmetic on void* is not standard C."
  - "`vec_push` copies elem_size bytes with memcpy. Grow by DOUBLING when full, not by one: growing by one makes n appends O(n^2)."
  - "Guard the realloc: use a temporary, because on failure realloc returns NULL and the original block is still allocated."
  - "`vec_get` returns a void* into the buffer - the caller casts it. Return NULL for an out-of-range index rather than reading past the end."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **generic container** | one implementation that holds any type |
| **template** | C++'s way to write generic code; C has none |
| **element size** | how many bytes one element takes; all a `void *` container knows |
| **capacity** / **count** | slots allocated / slots used |
| **GCC extension** | a feature GCC allows that standard C does not, such as `void *` arithmetic |
| **doubling** | growing capacity by a factor of 2 when full |
| **amortised O(1)** | constant cost per operation on average, though some are expensive |
| **dynamic array** | an array that grows as you append |
| **leak on realloc failure** | `p = realloc(p, n)` loses the original pointer if it fails |
| **size overflow** | `cap * elem_size` wrapping round to a small number |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `gcc -std=c17 -Wall vec.c -o vec && ./vec` | builds and runs |

### C names

| Name | What it does |
|---|---|
| `void *data` | the raw element storage |
| `(char *)v->data + i * v->elem_size` | the address of element `i` |
| `memcpy(dst, src, elem_size)` | copies one element in or out |
| `void *bigger = realloc(...); if (!bigger) return 0;` | the guarded realloc |
| `qsort`, `bsearch` | standard functions that already work on element size and raw bytes |

---

C has no templates. Generic containers are built from an element **size** and
raw bytes, which is exactly what `qsort` and `bsearch` already do.

```c
struct Vec {
    void  *data;
    size_t elem_size;
    size_t count;
    size_t capacity;
};
```

Nothing records the *type* — only how big one element is. That is the trade:
one implementation for every type, and no compiler check that you put ints in
and take ints out.

## Pointer arithmetic on void*

```c
(char *)v->data + i * v->elem_size
```

`void *` arithmetic is a GCC extension, not standard C. Cast to `char *`
first — a `char` is one byte by definition, so the arithmetic is plain bytes.

## Doubling

```c
if (v->count == v->capacity) {
    size_t cap = v->capacity ? v->capacity * 2 : 4;
    ...
}
```

Growing by a constant makes *n* appends O(n²) — each growth copies everything.
Doubling makes it **amortised O(1)**: the copies are 1 + 2 + 4 + ... + n, which
is less than 2n in total, so the average cost per append is constant even
though individual appends occasionally cost a lot.

That argument is worth being able to reproduce; it is why every dynamic array
in every language grows multiplicatively.

## Guarding realloc

```c
void *bigger = realloc(v->data, cap * v->elem_size);
if (!bigger) return 0;        /* v->data is still valid and still ours */
v->data = bigger;
```

Assigning straight back loses the original pointer on failure, and with it the
memory. The temporary is not style; it is the difference between a failed
append and a leak.

## Overflow in the size calculation

`cap * elem_size` can overflow `size_t` for large values, and the result is a
small allocation followed by writes past the end. Production code checks; this
lesson notes it so you know the check exists.

## Your turn

In `vec.h` and `vec.c`:

- `int vec_init(struct Vec *v, size_t elem_size)`
- `int vec_push(struct Vec *v, const void *elem)` — 1 or 0, doubling
- `void *vec_get(const struct Vec *v, size_t index)` — NULL out of range
- `int vec_pop(struct Vec *v, void *out)` — 1 or 0
- `size_t vec_count(const struct Vec *v)`
- `void vec_free(struct Vec *v)`
