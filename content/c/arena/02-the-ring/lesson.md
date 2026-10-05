---
title: "Round 2: The ring"
summary: A fixed-size buffer that forgets its oldest value when it is full. Indexes, wrap-around and no malloc.
order: 2
files: [ring.c, ring.h]
run: gcc -std=c17 -Wall -c ring.c
challenge:
  minutes: 18
  xp: 200
  requires:
    xp: 300
---

A sensor produces readings faster than anyone reads them. Keep the newest
four and let the oldest fall off.

## The task

`ring.h` defines the struct and declares five functions. Define them in
`ring.c`. Do not change the header.

```c
#define RING_CAP 4

typedef struct {
    int data[RING_CAP];
    int head;   /* index of the oldest value */
    int count;  /* how many values are stored */
} Ring;
```

- `void ring_init(Ring *r)` makes the ring empty.
- `int ring_push(Ring *r, int value)` adds a value as the newest. If there
  was room it returns `1`. If the ring was full, the value **replaces the
  oldest one** and it returns `0`; the count stays at `RING_CAP`.
- `int ring_pop(Ring *r, int *out)` removes the oldest value, stores it in
  `*out` and returns `1`. On an empty ring it returns `0` and leaves `*out`
  alone.
- `int ring_peek(const Ring *r, int index, int *out)` reads without
  removing: index `0` is the oldest value, `count - 1` the newest. It returns
  `1`, or `0` (leaving `*out` alone) when there is no such index.
- `int ring_count(const Ring *r)` is how many values are stored.

```text
push 1, 2, 3, 4      ring holds 1 2 3 4
push 5               ring holds 2 3 4 5   (returns 0: the 1 was overwritten)
pop                  gives 2, ring holds 3 4 5
```

The values live in `data` in a circle: the slot after index `RING_CAP - 1`
is index `0`.
