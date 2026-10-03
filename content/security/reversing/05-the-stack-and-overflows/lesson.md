---
title: The stack, and why overflows matter
summary: Where a function keeps its locals and its return address, what writing past a buffer corrupts, and the defences that exist because of it.
order: 5
files: [stackframe.py]
run: python stackframe.py
hints:
  - "On x86-64 a stack frame is laid out as: the buffer, then the 8-byte saved base pointer, then the 8-byte return address."
  - "`offset_to_return`: the number of bytes from the start of the buffer to the return address is `buffer_size + 8` (past the buffer and the saved base pointer)."
  - "`overflows_buffer`: input longer than the buffer overflows it."
  - "`reaches_return_address`: input long enough to write past the buffer and the saved base pointer, i.e. longer than `buffer_size + 8`."
---

The dangerous functions from the last lesson are dangerous for one concrete
reason: they let input write past the end of a buffer, and of **what is next to
that buffer in memory**. On the stack, what is next to it is the information the
CPU needs to return from the function - which is why an unbounded write can take
over a program.

> This lesson is about *understanding* the risk - the layout and the arithmetic.
> It stops there deliberately: recognising and preventing the bug is the goal,
> not building a working exploit.

## The stack frame

When a function runs, its local variables live on the **stack**. On x86-64 a
frame with a buffer looks like this, from lower addresses to higher:

```text
[ buffer (N bytes) ][ saved base pointer (8) ][ return address (8) ]
```

A write into the buffer that does not stop at `N` bytes keeps going **up** into
the saved base pointer, and then into the **return address** - the location the
CPU jumps to when the function finishes. Overwrite the return address and you
have changed where the program goes next. That is the entire mechanism behind
the classic stack buffer overflow, and it is why `gets` into a fixed buffer is
catastrophic: the attacker controls how far the write goes.

In this idealised layout the distances are simple arithmetic: it takes `N`
bytes to fill the buffer, 8 more to cover the saved base pointer, and the next 8
are the return address. The exercise below uses exactly that model.

Real binaries add to it. The compiler pads the frame for alignment, places other
local variables around the buffer, and - with a stack canary - inserts another 8
bytes before the saved base pointer. Built with `gcc -O0`, a function holding a
64-byte buffer had its return address **88** bytes away, not the 72 the model
predicts. Analysts therefore *measure* the offset in a debugger rather than
compute it; the model is for understanding why the overflow works, not for
predicting a particular binary.

## Why your programs are (mostly) safe now

Three defences, layered, make this far harder than it was in the 1990s:

- **Stack canaries** - a random value placed before the return address and
  checked on exit; an overflow smashes it and the program aborts.
- **NX / DEP** - the stack is non-executable, so injected code there will not run.
- **ASLR** - addresses are randomised each run (the PIE from lesson one), so the
  attacker cannot predict where anything is.

None of them fix the underlying bug - they raise the cost of exploiting it. The
real fix is still the previous lesson: do not write past the buffer.

## Your turn

In `stackframe.py` (x86-64, sizes in bytes):

- `offset_to_return(buffer_size)` - bytes from the buffer's start to the return
  address
- `overflows_buffer(input_len, buffer_size)` - does the input exceed the buffer?
- `reaches_return_address(input_len, buffer_size)` - is the input long enough to
  reach the return address?
