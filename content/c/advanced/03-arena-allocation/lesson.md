---
title: Arena allocation
summary: Allocating by bumping a pointer and freeing everything at once - the strategy that removes a whole class of lifetime bug.
order: 3
files: [arena.c, arena.h]
run: gcc -std=c17 -Wall arena.c -o arena && ./arena
hints:
  - "The arena is one malloc plus an offset. `arena_alloc` rounds the offset up for alignment, checks it fits, returns the pointer and advances."
  - "Align with `(offset + align - 1) & ~(align - 1)` where align is a power of two - that rounds up to the next multiple."
  - "Use `_Alignof(max_align_t)` as the alignment so anything can be stored. Include <stddef.h> and <stdalign.h>."
  - "`arena_reset` sets the offset back to 0 and frees nothing - reusing the same block is the entire point."
---

`malloc` and `free` track every block individually so any one can be returned
at any time. When a set of allocations all die together, that bookkeeping is
paid for nothing.

An **arena** allocates one block up front and hands out pieces by bumping an
offset:

```c
struct Arena {
    unsigned char *base;
    size_t capacity;
    size_t offset;
};
```

`alloc` is a few instructions. There is no per-allocation `free` at all —
`arena_reset` sets the offset to zero, and everything is gone.

## Where it fits

- **A request in a server.** Allocate from an arena, reset when the response is
  sent. Nothing can leak, because nothing is freed individually.
- **A compiler pass.** AST nodes live until the pass ends.
- **A frame in a game.** Reset every frame.

The shared property is a **clear point where everything dies**. Where that
exists, an arena removes leaks, double frees and use-after-free in one move:
there are no individual frees to get wrong.

Where it does not exist, an arena is the wrong tool — it cannot reclaim one
object, so a long-lived arena with churn just grows.

## Alignment

```c
size_t aligned = (offset + align - 1) & ~(align - 1);
```

A `double` on most platforms must sit at an address divisible by 8;
misaligned access is undefined behaviour and on some architectures a crash.
Rounding up to the next multiple of the alignment is the whole job, and the
bit trick works because alignments are powers of two.

`_Alignof(max_align_t)` is the strictest alignment any standard type needs, so
using it means anything can be stored.

## The trade

You give up individual frees and you give up growth — the block is fixed, so
an allocation that does not fit fails. Both are acceptable exactly when the
lifetime story is simple, and unacceptable otherwise. That is the judgement,
and it is why arenas are a tool rather than a replacement.

## Your turn

In `arena.h` and `arena.c`:

- `int arena_init(struct Arena *a, size_t capacity)`
- `void *arena_alloc(struct Arena *a, size_t size)` — aligned, NULL when full
- `char *arena_strdup(struct Arena *a, const char *s)`
- `size_t arena_used(const struct Arena *a)`
- `void arena_reset(struct Arena *a)` — reuse, free nothing
- `void arena_free(struct Arena *a)`
