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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **ring buffer** | a fixed array used in a circle; the oldest value is overwritten when full |
| **head** | the index of the oldest value |
| **count** | how many values are stored |
| **wrap around** | the slot after the last index is index 0 |
| **peek** | read without removing |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `gcc -std=c17 -Wall -c ring.c` | compiles to check it builds |

### C names

| Name | What it does |
|---|---|
| `#define RING_CAP 4` | the capacity |
| `typedef struct { ... } Ring;` | the ring type |
| `(head + i) % RING_CAP` | the index `i` places after `head`, wrapping round |
| `int *out` | where a removed or peeked value is written |

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
