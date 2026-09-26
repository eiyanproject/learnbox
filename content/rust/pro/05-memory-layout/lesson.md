---
title: Memory layout and allocation
summary: Size, alignment and padding; niche optimisation; where data lives; and cutting allocations in hot code.
order: 5
files: [src/lib.rs]
run: cargo test
hints:
  - "`Packed` orders fields big to small (`u64`, `u32`, `u16`, `u8`), so padding disappears: `size_of::<Packed>()` is 16 while the naive order is 24."
  - "`sum_digits(s)` must not allocate: iterate `s.bytes()` and use `b.is_ascii_digit()` with `(b - b'0') as u64`, instead of building a Vec or a String."
  - "`join_with_capacity`: sum the lengths first, `String::with_capacity(total)`, then push, so the buffer is allocated once."
  - "`normalize(s) -> Cow<str>` returns `Cow::Borrowed(s.trim())` when there is nothing else to change, and only allocates when the text contains uppercase letters."
---

## Size, alignment, padding

Every type has a **size** and an **alignment**; a value's address must be a
multiple of its alignment, so **padding** is inserted between fields to keep
each one aligned. Declaration order can therefore change the size - but only
when you have taken the ordering into your own hands:

```rust
#[repr(C)] struct Wasteful { a: u8, b: u64, c: u8 }  // 24: 7 padding after a, 7 at the end
#[repr(C)] struct Tight    { b: u64, a: u8, c: u8 }  // 16: no gaps
```

The `#[repr(C)]` is doing the work in that example. **Without it, both of those
are 16 bytes**, because the layout of a plain `struct` is unspecified and the
compiler already reorders fields to pack them for you. You cannot even rely on
the order being what you wrote:

```rust
struct Wasteful { a: u8, b: u64, c: u8 }   // 16 bytes - reordered for you
```

So the rule is not "always put the big fields first". It is: let the compiler
lay out your types, and reach for `#[repr(C)]` only when the layout must match
something outside Rust - an FFI struct, a file format, a wire protocol. At that
point the order is fixed, the padding becomes yours to manage, and putting the
largest fields first is how you keep it small.

```rust
use std::mem::{align_of, size_of};
size_of::<u64>()            // 8
align_of::<Tight>()         // 8
size_of::<Option<u8>>()     // 2
size_of::<Option<&u8>>()    // 8: no extra byte needed
```

## Niche optimisation

`Option<&T>`, `Option<Box<T>>` and `Option<NonZeroU32>` are the same size as the
value they wrap: a reference is never null, so "null" can represent `None`.
This is why idiomatic Rust can return `Option` freely in hot code.

## Stack, heap and pointers

Values live on the **stack** by default: cheap, freed automatically. Heap
allocation happens when you ask for it: `Box`, `Vec`, `String`, `Rc`, `HashMap`.

```rust
size_of::<[u8; 1024]>()     // 1024: the array is the value
size_of::<Vec<u8>>()        // 24: pointer, length, capacity
size_of::<Box<[u8]>>()      // 16: pointer and length, no capacity
size_of::<&[u8]>()          // 16: a fat pointer
size_of::<&dyn Trait>()     // 16: data pointer plus vtable pointer
```

`Vec<T>` keeps spare capacity so pushes are amortised; `into_boxed_slice()`
drops that slack when the collection stops growing.

## Cutting allocations

Allocation is the usual reason "fast-looking" Rust is slow:

- `String::with_capacity` / `Vec::with_capacity` when the final size is known
- iterate `&str` and `[u8]` instead of collecting into temporary `Vec`s
- `Cow<str>` to borrow when no change is needed (Intermediate: Strings)
- reuse one buffer across loop iterations (`buf.clear()`) instead of allocating each time
- `&[T]` and `&str` parameters instead of `Vec<T>` and `String`

Measure before optimising: `cargo build --release`, then time the real workload.
A debug build is several times slower and says nothing about release performance.

## Your turn

In `src/lib.rs`:

- `Packed`: the same four fields as `Wasteful` (a `u8`, a `u16`, a `u32`, a `u64`)
  ordered so that `size_of::<Packed>() == 16`, with `Packed::new(a, b, c, d)`
- `sum_digits(s)`: sum the ASCII digits in a string **without allocating**
- `join_with_capacity(parts, sep)`: join strings with exactly one allocation
- `normalize(s)`: trim and lower-case, borrowing when the input needs no change
- `count_words_reusing_buffer(lines)`: count words per line, reusing a single
  `String` buffer across iterations
