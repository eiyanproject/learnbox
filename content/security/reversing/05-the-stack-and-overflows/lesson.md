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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **memory** | where a running program keeps its code and data, each byte at an address |
| **the stack** | the area of memory where functions keep their local variables while they run |
| **stack frame** | one function's part of the stack |
| **local variable** | a variable that exists only while its function runs, such as `char buf[16]` |
| **buffer** | a fixed-size area for data, such as text |
| **lower / higher addresses** | positions in memory; here the buffer is lower, the return address higher |
| **saved base pointer** | 8 bytes the function keeps for its caller, just above the locals (on x86-64) |
| **return address** | 8 bytes saying where the program continues when this function finishes |
| **stack buffer overflow** | a write that runs past a buffer on the stack and over what is above it |
| **offset** | a distance in bytes, here from the start of the buffer |
| **model** | a simplified picture; real frames add padding and other variables |
| **padding** | unused bytes the compiler adds to keep things aligned |
| **debugger** | a tool such as `gdb` that pauses a program and shows its memory |
| **stack canary** (stack protector) | a random value placed before the return address and checked when the function returns |
| **NX** (no-execute), **DEP** | memory holding data, such as the stack, is marked as not runnable |
| **ASLR** | addresses are randomised every run (Reversing lesson 1) |
| **mitigation** | a defence that makes a bug harder to abuse without fixing the bug |
| **abort** | the program stops itself at once, rather than carry on in a broken state |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `gcc -fstack-protector-strong -o prog prog.c` | compiles with stack canaries (usually on by default) |
| `readelf -lW prog \| grep GNU_STACK` | shows the stack's permissions; `RW` without `E` means NX is on |
| `python stackframe.py` | runs your program: where the return address is for a 64-byte buffer |

### Python names

| Name | What it does |
|---|---|
| `SAVED_BP = 8` | given to you: the size of the saved base pointer, in bytes |
| `buffer_size + SAVED_BP` | the offset of the return address in the lesson's model |
| `input_len > buffer_size` | the input does not fit in the buffer |

---

The dangerous functions of the last lesson are dangerous for one concrete
reason: they let input write past the end of a buffer, onto **what is stored
next to it in memory**. On the stack, what is next to it is the information
the processor needs to return from the function. That is why one unbounded
write can take over a whole program.

This lesson is about **understanding** the risk: the layout and the
arithmetic, and the defences built because of it. It stops there on purpose.
The goal is to recognise and prevent the bug, not to build an attack.

## The stack frame

While a function runs, its local variables live on **the stack**. On x86-64,
a function with one buffer has a **stack frame** like this, from lower
addresses to higher:

```text
[ buffer (N bytes) ][ saved base pointer (8) ][ return address (8) ]
```

- The **buffer** holds the data, such as text that was read in.
- The **saved base pointer** is bookkeeping for the function that called this
  one.
- The **return address** says where the program carries on when this function
  finishes.

Writes into the buffer go **upwards**, towards higher addresses. A write that
does not stop at `N` bytes keeps going, into the saved base pointer and then
into the return address. When the function finishes, the processor goes to
whatever address is stored there. If input overwrote it, input has changed
where the program goes next.

That is the whole mechanism behind the classic **stack buffer overflow**, and
it is why `gets` into a fixed buffer is so serious: the input decides how far
the write goes.

## The arithmetic

In this simplified **model**, the distances are simple:

- `N` bytes fill the buffer;
- 8 more cover the saved base pointer;
- the next 8 are the return address.

So the return address starts at **offset** `N + 8` from the start of the
buffer. For a 64-byte buffer, that is 72. Input of 64 bytes or fewer fits;
65 or more overflows the buffer; more than 72 reaches the return address.

Real programs differ from the model. The compiler adds **padding**, places
other local variables around the buffer, and, with a stack canary, puts 8
more bytes before the saved base pointer. In one real build with `gcc -O0`, a
function holding a 64-byte buffer had its return address **88** bytes away,
not the 72 the model predicts. So analysts **measure** the offset in a
**debugger** rather than calculate it. The model is for understanding why an
overflow is dangerous, not for predicting a particular program.

## Why modern programs are (mostly) protected

Three layered defences, all usually on by default today, make this much
harder than it was in the 1990s:

| Defence | What it does |
|---|---|
| **stack canary** | a random value placed before the return address and checked just before the function returns; if an overflow changed it, the program aborts |
| **NX** (also called DEP) | the stack is marked as data, not code, so bytes written there cannot be run as instructions |
| **ASLR** | addresses change every run (the PIE of Reversing lesson 1), so nothing is where an attacker expects |

You can see the canary work. Here is a small program that copies its argument
into a 16-byte buffer with `strcpy`, built with `-fstack-protector-strong`,
then given 40 characters:

```text
$ ./canary hello
hello
$ ./canary AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
*** stack smashing detected ***: terminated
Aborted (core dumped)
```

The canary was overwritten, the check failed, and the program stopped before
it could return to a corrupted address. And `readelf -lW canary | grep
GNU_STACK` shows the stack's permissions as `RW`: readable and writable, with
no `E` for execute, so NX is on.

These are **mitigations**: none of them fixes the bug. The program still
crashed; an attacker who can find a way around one defence still has a
working bug to use. The real fix is still the last lesson's: never write past
the buffer. Use `fgets` and `snprintf`, with the buffer's size.

## Your turn

In `stackframe.py` (x86-64, the lesson's model, sizes in bytes):

- `offset_to_return(buffer_size)`: the bytes from the start of the buffer to
  the return address.
- `overflows_buffer(input_len, buffer_size)`: does the input exceed the
  buffer?
- `reaches_return_address(input_len, buffer_size)`: is the input long enough
  to reach the return address?

Run it:

```text
a 64-byte buffer: return address at offset 72
72 bytes reaches it? False
```

72 bytes fill the buffer and the saved base pointer exactly; only the 73rd
would touch the return address.

## Check yourself

1. What does the return address hold?
   *Where the program continues when the function finishes.*
2. In the model, how far from a 32-byte buffer's start is the return address?
   *40 bytes: 32 + 8.*
3. Why measure the offset in a debugger instead of calculating it?
   *Real frames add padding, other variables and the canary.*
4. What does a stack canary do when an overflow changes it?
   *The check fails and the program aborts.*
5. Do these defences fix the bug?
   *No: they make it harder to abuse. Bounded functions fix it.*
