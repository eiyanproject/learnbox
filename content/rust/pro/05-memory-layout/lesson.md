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

Fast code is mostly about memory: how big values are, where they live, and
how often the program asks the operating system's allocator for more. This
lesson looks at what Rust values actually look like in memory, and at the
habits that keep hot code from allocating. The exercise's tests use a
counting allocator, so they can check not only that your functions give the
right answer, but how many times they allocated getting there.

## Size, alignment, padding

Every type has a **size**, the bytes one value takes, and an **alignment**:
a value's address must be a multiple of its alignment, because processors
read memory fastest (and some processors only) in aligned chunks. A `u64` has
alignment 8, so it must start at an address divisible by 8; a `u8` has
alignment 1 and can go anywhere. `std::mem::size_of::<T>()` and
`align_of::<T>()` report both.

In a struct, each field must be aligned too, so the compiler inserts unused
**padding** bytes where needed, and pads the end so that values in an array
stay aligned. With the field order fixed as written, that can waste a lot:

```rust
#[repr(C)] struct Wasteful { a: u8, b: u64, c: u8 }  // 24 bytes
#[repr(C)] struct Tight    { b: u64, a: u8, c: u8 }  // 16 bytes
```

```text
 Wasteful (#[repr(C)]):
  offset 0   a  [x . . . . . . .]   1 byte, then 7 of padding so b is aligned to 8
  offset 8   b  [x x x x x x x x]
  offset 16  c  [x . . . . . . .]   1 byte, then 7 of padding so the size is a multiple of 8
                                    total 24, of which 14 are padding

 Tight (#[repr(C)]):
  offset 0   b  [x x x x x x x x]
  offset 8   a  [x]
  offset 9   c  [x . . . . . .]     6 bytes of padding at the end
                                    total 16
```

The `#[repr(C)]` is doing the work in that example. **Without it, both
structs are 16 bytes**, because the layout of a plain Rust `struct` is
unspecified and the compiler already reorders fields to pack them tightly.
You cannot even rely on the fields being in the order you wrote:

```rust
struct Wasteful { a: u8, b: u64, c: u8 }   // 16 bytes: reordered for you
```

So the rule is not "always put the big fields first". It is: let the
compiler lay out your types, and reach for `#[repr(C)]` only when the layout
must match something outside Rust: a C struct in FFI (lesson 7), a file
format, a network protocol. `#[repr(C)]` means "lay this out exactly as C
would: fields in the order written, with C's padding rules". At that point
the order is yours, and so is the padding; putting the largest fields first
is how you keep it small. The exercise is exactly that case.

## Niche optimisation

An `Option<u8>` needs room for 256 `u8` values plus `None`, so it takes 2
bytes: one for the value, one to say which variant it is. But an
`Option<&u8>` is the same size as a `&u8`, 8 bytes, with no extra byte at
all. Why?

A reference can never be null, so the all-zero bit pattern is never a valid
`&u8`. The compiler uses that unused pattern, a **niche**, to represent
`None`. The same goes for `Box<T>` (never null), `NonZeroU32` (never 0),
`bool` (only 0 and 1 are used), and enums with spare values. This is why
idiomatic Rust can use `Option<&T>` and `Option<Box<T>>` freely: they cost
exactly as much as a nullable pointer in C, while making the null case
impossible to forget.

## Stack, heap and pointers

Values live on the **stack** by default: allocating is free (the function's
stack frame is set up anyway), and freeing is automatic when the function
returns. Heap memory (Beginner lesson 4) is used only when you ask for it,
through `Box`, `Vec`, `String`, `Rc`, `HashMap` and other owning types.
What is on the stack is then just the **handle**:

```rust
size_of::<[u8; 1024]>()     // 1024: the array is the value itself, on the stack
size_of::<Vec<u8>>()        // 24: pointer, length, capacity; the bytes are on the heap
size_of::<Box<[u8]>>()      // 16: pointer and length, no capacity
size_of::<&[u8]>()          // 16: a fat pointer: address and length
size_of::<&dyn Trait>()     // 16: data pointer plus vtable pointer (Advanced lesson 10)
```

(Expressions with their values on a 64-bit machine.) A `Vec<T>` keeps spare
**capacity** so that repeated `push`es do not reallocate every time: when it
runs out, it allocates a bigger block (typically double) and copies
everything across, so pushes are cheap *on average*. `into_boxed_slice()`
drops the spare capacity once a collection stops growing, saving the
capacity field and the unused space.

## Cutting allocations

Each heap allocation is a call into the allocator, usually tens of
nanoseconds, plus the later free, plus worse cache behaviour from data spread
around memory. In hot code, it is the most common reason that "fast-looking"
Rust is slow. The usual remedies:

- **Pre-size**: when the final size is known, `String::with_capacity(n)` or
  `Vec::with_capacity(n)` allocate once, instead of growing (and
  reallocating) several times along the way.
- **Iterate, do not collect**: `s.bytes()`, `s.chars()` and slice iterators
  read in place; collecting into a temporary `Vec` or `String` just to loop
  over it again allocates for nothing. The starter's `sum_digits` collects
  twice.
- **Borrow when nothing changes**: return `Cow<str>` (Intermediate lesson 7),
  borrowing the input in the common case.
- **Reuse buffers**: one `String` or `Vec` created before a loop and
  `clear()`ed on each turn keeps its capacity, so after the first few turns
  it never allocates again. Creating a new one inside the loop allocates on
  every turn.
- **Take slices**: `&[T]` and `&str` parameters instead of `Vec<T>` and
  `String`, so callers do not have to allocate to call you.

Measure before optimising: `cargo build --release`, then time the real
workload. A debug build is often ten times slower, and its timings say
nothing about the release build.

### How the tests count allocations

Rust lets a program replace its **global allocator**, the code behind every
`Box::new` and `Vec::push` that needs memory, with
`#[global_allocator]`. The exercise's tests install one that forwards to the
normal system allocator but adds 1 to a counter on every `alloc` and
`realloc`. They then call your function and compare the counter before and
after: `sum_digits` must allocate 0 times, `join_with_capacity` exactly once,
`normalize` 0 times for text that needs no change, and
`count_words_reusing_buffer` at most 4 times for 200 lines.
(`std::hint::black_box` stops the optimiser from removing a call whose result
is unused.)

## Every size above, checked

```rust
use std::mem::{align_of, size_of};
use std::num::NonZeroU32;

#[allow(dead_code)]
#[repr(C)]
struct WastefulC { a: u8, b: u64, c: u8 }

#[allow(dead_code)]
#[repr(C)]
struct Tight { b: u64, a: u8, c: u8 }

#[allow(dead_code)]
struct Wasteful { a: u8, b: u64, c: u8 }      // no repr: the compiler reorders

trait Trait {}

fn main() {
    println!("{} {} {}", size_of::<WastefulC>(), size_of::<Tight>(), size_of::<Wasteful>());
    println!("{} {}", size_of::<u64>(), align_of::<Tight>());
    println!("{} {}", size_of::<Option<u8>>(), size_of::<Option<&u8>>());
    println!("{} {} {}", size_of::<Option<Box<u8>>>(), size_of::<Option<NonZeroU32>>(), size_of::<Option<u32>>());
    println!(
        "{} {} {} {} {}",
        size_of::<[u8; 1024]>(),
        size_of::<Vec<u8>>(),
        size_of::<Box<[u8]>>(),
        size_of::<&[u8]>(),
        size_of::<&dyn Trait>()
    );
}
```

```output
24 16 16
8 8
2 8
8 4 8
1024 24 16 16 16
```

The same three fields take 24 bytes in C order and 16 when the compiler may
reorder. A struct's alignment is its largest field's, 8 here.
`Option<NonZeroU32>` is 4 bytes and `Option<u32>` is 8: zero is free to mean
`None` only when the value can never be zero, and otherwise the variant needs
its own space, padded to `u32`'s alignment of 4.

## Your turn

In `src/lib.rs`:

- `Packed`: the same four fields as `Wasteful` (a `u8`, a `u64`, a `u16` and
  a `u32`), still `#[repr(C)]`, but in an order that makes
  `size_of::<Packed>() == 16`, with the same names. `Packed::new(a, b, c, d)`
  keeps its parameter order. (`Wasteful` is 24: work out where its padding
  goes, as in the diagram.)
- `sum_digits(s)`: the sum of the ASCII digits in `s` (`"a1b2c3"` gives 6),
  with **zero** allocations: loop over the bytes directly
- `join_with_capacity(parts, sep)`: the parts joined with `sep` between them
  (`"a, b, c"`; `""` for no parts), allocating exactly **once**: add up the
  lengths of the parts and separators first, then `String::with_capacity`
- `normalize(s) -> Cow<str>`: `s` trimmed and lower-cased. When the trimmed
  text has no upper-case ASCII letters, return it **borrowed**, a slice of
  `s`, with no allocation: `"  padded  "` gives `Cow::Borrowed("padded")`.
  Only text like `"  Mixed Case  "` becomes `Cow::Owned("mixed case")`.
- `count_words_reusing_buffer(lines)`: the number of words on each line
  (`["one two", "  three  ", "", "four five six"]` gives `[2, 1, 0, 3]`),
  processing each line through **one** `String` buffer created before the
  loop and `clear()`ed each turn, and a result `Vec` created with the right
  capacity
