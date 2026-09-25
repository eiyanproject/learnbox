---
title: Bit manipulation and flags
summary: Packing booleans into an integer, the shift and mask idioms, and the undefined behaviour hiding in a shift.
order: 4
files: [bits.c, bits.h]
run: gcc -std=c17 -Wall bits.c -o bits && ./bits
hints:
  - "`set_flag` is `value | flag`; `clear_flag` is `value & ~flag`; `toggle_flag` is `value ^ flag`; `has_flag` is `(value & flag) != 0`."
  - "Return `(value & flag) != 0` rather than `value & flag` - the second returns the flag's value, not 1, and comparing it to 1 then fails."
  - "`count_bits` can shift right and test the low bit, or use the Kernighan trick: `n &= n - 1` clears the lowest set bit, so the loop runs once per set bit."
  - "`extract_byte` shifts right by index * 8 and masks with 0xFF. Use unsigned types throughout: shifting a negative signed value is undefined."
---

Bits are worth understanding for flags, protocols, file formats, hashing and
anything talking to hardware.

## The operators

| | | |
|---|---|---|
| `&` | AND | keeps bits set in both — masking |
| `\|` | OR | sets bits — combining flags |
| `^` | XOR | flips bits set in the operand — toggling |
| `~` | NOT | inverts every bit |
| `<<` | left shift | multiply by 2ⁿ |
| `>>` | right shift | divide by 2ⁿ |

## Flags

```c
#define READ  (1u << 0)     /* 0001 */
#define WRITE (1u << 1)     /* 0010 */
#define EXEC  (1u << 2)     /* 0100 */

unsigned perms = READ | WRITE;      /* set */
perms |= EXEC;                      /* add */
perms &= ~WRITE;                    /* remove */
perms ^= READ;                      /* toggle */
if (perms & EXEC) { ... }           /* test */
```

`1u << n` rather than a literal: the intent is visible and the compiler
computes it.

**Return a boolean, not the bit.** `value & EXEC` is `4`, not `1`. A function
declared to return 0 or 1 must write `(value & flag) != 0`, or callers
comparing against `1` get the wrong answer.

## Shifts have undefined cases

- Shifting by **more than the width** of the type is undefined — including by
  exactly 32 for a 32-bit int, which is the easy mistake.
- Shifting a **negative** value left is undefined.
- Shifting a negative value **right** is implementation-defined (almost always
  an arithmetic shift, but not guaranteed).

Use `unsigned` for anything involving bits. The rules are all simpler there,
and overflow is defined.

## The Kernighan trick

```c
while (n) { n &= n - 1; count++; }
```

`n - 1` flips the lowest set bit and everything below it, so the AND clears
exactly that bit. The loop runs once per set bit rather than once per bit
position — a neat thing to have seen, even though `__builtin_popcount` is what
you would actually call.

## Your turn

In `bits.h` and `bits.c`, with flags `FLAG_READ`, `FLAG_WRITE`, `FLAG_EXEC`:

- `unsigned set_flag(unsigned value, unsigned flag)`
- `unsigned clear_flag(unsigned value, unsigned flag)`
- `unsigned toggle_flag(unsigned value, unsigned flag)`
- `int has_flag(unsigned value, unsigned flag)` — 0 or 1
- `int count_bits(unsigned value)`
- `unsigned extract_byte(unsigned value, int index)` — byte 0 is the lowest
