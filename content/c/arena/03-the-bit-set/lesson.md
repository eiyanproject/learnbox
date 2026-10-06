---
title: "Round 3: The bit set"
summary: 256 flags packed into 32 bytes. Shifts, masks and a population count, with no library to lean on.
order: 3
files: [bitset.c, bitset.h]
run: gcc -std=c17 -Wall -c bitset.c
challenge:
  minutes: 20
  xp: 250
  requires:
    xp: 420
---

The scheduler tracks which of 256 job slots are taken. An array of 256
`int`s is a kilobyte per table; packed into bits it is 32 bytes.

## The task

`bitset.h` defines the struct and declares the functions. Define them in
`bitset.c`. Do not change the header.

```c
#define BITSET_BITS 256

typedef struct {
    unsigned char bytes[BITSET_BITS / 8];
} BitSet;
```

Bit `n` lives in `bytes[n / 8]`, at position `n % 8` counting from the least
significant bit. So bit 0 is the value `1` in `bytes[0]`, bit 7 is the value
`128` in `bytes[0]`, and bit 8 is the value `1` in `bytes[1]`.

- `void bs_clear_all(BitSet *s)` turns every bit off.
- `int bs_set(BitSet *s, int n)` turns bit `n` on.
- `int bs_clear(BitSet *s, int n)` turns bit `n` off.
- `int bs_test(const BitSet *s, int n)` is `1` if bit `n` is on, `0` if it
  is off.
- `int bs_count(const BitSet *s)` is how many bits are on.
- `int bs_next(const BitSet *s, int from)` is the number of the first bit
  that is on at position `from` or later, or `-1` if there is none. A `from`
  below 0 searches from 0.
- `void bs_union(BitSet *dst, const BitSet *src)` turns on in `dst` every
  bit that is on in `src`.
- `void bs_intersect(BitSet *dst, const BitSet *src)` leaves on in `dst`
  only the bits that are on in both.

`bs_set`, `bs_clear` and `bs_test` return `-1`, and change nothing, when `n`
is not between 0 and `BITSET_BITS - 1`. Otherwise `bs_set` and `bs_clear`
return `0`.

```text
bs_set(&s, 3); bs_set(&s, 200);
bs_count(&s)        ->  2
bs_next(&s, 0)      ->  3
bs_next(&s, 4)      ->  200
bs_next(&s, 201)    ->  -1
```
