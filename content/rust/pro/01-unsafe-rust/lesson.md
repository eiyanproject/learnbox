---
title: Unsafe Rust
summary: Raw pointers, what unsafe actually permits, and wrapping it in a safe API whose invariants you can state.
order: 1
files: [src/lib.rs]
run: cargo test
hints:
  - "`split_at_mut`: `let len = slice.len(); let ptr = slice.as_mut_ptr(); assert!(mid <= len);` then in one `unsafe` block return `(slice::from_raw_parts_mut(ptr, mid), slice::from_raw_parts_mut(ptr.add(mid), len - mid))`."
  - "`swap_unchecked` is an `unsafe fn`: document the contract (`a` and `b` must be in bounds) and use `std::ptr::swap(ptr.add(a), ptr.add(b))`."
  - "`Buffer::push`: when `len == capacity`, grow to `max(8, capacity * 2)` (for example with `self.bytes.reserve_exact(...)`), then push. `extend` comes from `impl Extend<u8> for Buffer`, a loop calling `push`."
  - "`as_str` is safe only if the bytes really are UTF-8, so validate with `std::str::from_utf8` and return `Option<&str>`. `as_str_unchecked` is the `unsafe fn` version using `from_utf8_unchecked`."
---

Safe Rust guarantees that a program has no data races, never uses freed
memory, and never follows a dangling reference. The compiler proves this
with the ownership and borrowing rules. But those rules are conservative:
they reject some programs that are in fact correct, because the compiler
cannot see *why* they are correct.

Here is one. Splitting a slice into two mutable halves is correct,
since the halves do not overlap, yet the borrow checker refuses:

```rust
pub fn split_at_mut(slice: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    let len = slice.len();
    (&mut slice[..mid], &mut slice[mid..len])
}
```

```text
error[E0499]: cannot borrow `*slice` as mutable more than once at a time
 --> src/lib.rs:3:30
  |
1 | pub fn split_at_mut(slice: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
  |                            - let's call the lifetime of this reference `'1`
2 |     let len = slice.len();
3 |     (&mut slice[..mid], &mut slice[mid..len])
  |     -------------------------^^^^^-----------
  |     |     |                  |
  |     |     |                  second mutable borrow occurs here
  |     |     first mutable borrow occurs here
  |     returning this value requires that `*slice` is borrowed for `'1`
```

The checker sees two `&mut` borrows of `slice` at once, and does not reason
about index ranges. The same limitation appears when implementing `Vec`,
talking to C libraries, or writing low-level concurrency primitives. For
those cases, `unsafe` is how you tell the compiler: "I have checked this
myself; trust me here". The rest of this lesson is about what that promise
covers, and how to keep it.

## What unsafe actually allows

Inside an `unsafe { }` block you get exactly five extra abilities, sometimes
called the unsafe "superpowers":

1. dereference a **raw pointer** (`*const T`, `*mut T`)
2. call an `unsafe fn`, including functions from C (`extern "C"`)
3. implement an `unsafe trait`, such as `Send` and `Sync`
4. read or write a `static mut` (a global variable that can change)
5. read fields of a `union`

That is all. Every other rule still applies: types are checked, borrows of
normal references are checked, overflow still panics in debug builds.
`unsafe` does **not** turn off the borrow checker, and it is not "C mode".
Most code inside an `unsafe` block is ordinary Rust; only those five
operations become possible.

Each of them is an error outside `unsafe`, and the message says why it is
dangerous:

```text
error[E0133]: dereference of raw pointer is unsafe and requires unsafe block
 --> src/lib.rs:4:5
  |
4 |     *p += 1;
  |     ^^ dereference of raw pointer
  |
  = note: raw pointers may be null, dangling or unaligned; they can violate aliasing rules and cause data races: all of these are undefined behavior
```

## Raw pointers

A **raw pointer** is an address with no guarantees attached: `*const T`
(read-only) or `*mut T`. Creating one is safe; only dereferencing it is not:

```rust
let mut x = 5;
let p: *mut i32 = &mut x;         // a reference converts to a raw pointer: safe
unsafe { *p += 1; }               // following it: unsafe
```

(A fragment.) Unlike references, raw pointers may be null, may point at
freed memory, may be misaligned, and may **alias** (two `*mut` to the same
place are allowed). The compiler checks none of it. Breaking the rules
causes **undefined behaviour** (UB): not a panic, not an error, but a program
whose behaviour the language no longer defines. The optimiser assumes UB
never happens, so a program with UB may crash, may compute garbage, or may
work perfectly in testing and fail in production on a different compiler
version.

The rules you are promising to keep when you dereference:

- the pointer is non-null, correctly **aligned** for `T`, and points at a
  live value of type `T` that has been initialised;
- you do not create a `&mut` to memory while any other reference to the
  same memory is in use (the borrowing rule still holds for the references
  you make from pointers, even though the compiler cannot check it);
- every value is valid for its type: a `bool` is 0 or 1, a reference is
  never null, a `str` is UTF-8, an enum holds one of its variants.

## Safe wrappers: the whole point

The aim is to keep `unsafe` **contained**: write the smallest possible
unsafe core, check its preconditions in ordinary code, and offer a **safe**
function around it. If the safe function cannot be misused, however it is
called, it is called **sound**:

```rust
pub fn split_at_mut(slice: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    let len = slice.len();
    let ptr = slice.as_mut_ptr();
    assert!(mid <= len);                                  // the precondition, checked
    // SAFETY: mid <= len, so both ranges are inside the slice, and they do not overlap.
    unsafe {
        (
            std::slice::from_raw_parts_mut(ptr, mid),
            std::slice::from_raw_parts_mut(ptr.add(mid), len - mid),
        )
    }
}
```

Step by step:

1. `slice.as_mut_ptr()` gives a `*mut i32` to the first element. From here
   on the borrow checker no longer tracks it.
2. `assert!(mid <= len)` is the safety check. Without it, a call with
   `mid = 10` on a 3-element slice would produce a slice pointing past the
   end: UB. With it, that call panics instead, which is safe.
3. `ptr.add(mid)` moves the pointer `mid` elements along (an `unsafe fn`: the
   result must stay inside the same allocation).
4. `slice::from_raw_parts_mut(ptr, n)` builds a `&mut [i32]` of `n` elements
   starting at `ptr` (also `unsafe`: you promise those `n` elements exist
   and nothing else references them).

The two returned slices cover `0..mid` and `mid..len`: in bounds and
disjoint, so having two `&mut` is correct. The lifetime of both is tied to
the input `slice` by elision, so the borrow checker still makes sure the
caller cannot use the original slice while the halves are alive.

```text
 slice:  [ 0 | 1 | 2 | 3 | 4 ]       mid = 2
           ^       ^
           ptr     ptr.add(2)
         [ first  ][ second    ]     two &mut, no overlap
```

The standard library's own `slice::split_at_mut` is written this way, and
that is the normal pattern: `Vec`, `String`, `HashMap` and `Rc` all have
small unsafe cores behind safe interfaces.

## Unsafe functions

When a function **cannot** check its own preconditions, cheaply or at all,
mark it `unsafe fn`. Then every caller must write `unsafe` to call it, which
makes the caller responsible, and the contract is written in a
`# Safety` section of the documentation comment:

```rust
/// # Safety
/// `index` must be less than `slice.len()`.
pub unsafe fn get_unchecked(slice: &[i32], index: usize) -> i32 {
    // SAFETY: the caller promises index < slice.len(), so the pointer stays in bounds.
    unsafe { *slice.as_ptr().add(index) }
}
```

Two different things are going on, and it helps to keep them apart:

- `unsafe fn` says "**callers** must uphold a contract". It restricts who may
  call the function.
- `unsafe { }` says "**I** have upheld the contract of the unsafe operations
  inside". It is where the checking happens.

In the 2024 edition, the body of an `unsafe fn` is *not* automatically an
unsafe block: the operations inside still need their own `unsafe { }`, with
their own justification. Leave it out and the compiler warns:

```text
warning[E0133]: dereference of raw pointer is unsafe and requires unsafe block
  |
4 |     *slice.as_ptr().add(index)
  |     ^^^^^^^^^^^^^^^^^^^^^^^^^^ dereference of raw pointer
  |
note: an unsafe function restricts its caller, but its body is safe by default
```

## Rules of thumb

- Reach for `unsafe` only when safe Rust genuinely cannot express the code,
  or a **measured** hot spot needs it. Splitting borrows, building
  collections, and FFI (lesson 7) are the classic reasons; "the borrow
  checker is annoying" is not.
- Every `unsafe` block gets a comment, by convention starting `// SAFETY:`,
  saying **why it is sound**: which preconditions hold and what guarantees
  them. If you cannot write that comment, the code is probably not sound.
  The exercise's tests count these comments.
- Test under **Miri** (`cargo +nightly miri test`) when you can: an
  interpreter for Rust that detects many kinds of undefined behaviour that
  normal tests miss, such as out-of-bounds pointer use and aliasing
  violations.

## Run it

```rust
fn split_at_mut(slice: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    let len = slice.len();
    let ptr = slice.as_mut_ptr();
    assert!(mid <= len);
    // SAFETY: mid <= len, so both halves are in bounds, and they do not overlap.
    unsafe {
        (
            std::slice::from_raw_parts_mut(ptr, mid),
            std::slice::from_raw_parts_mut(ptr.add(mid), len - mid),
        )
    }
}

/// # Safety
/// `index` must be less than `slice.len()`.
unsafe fn get_unchecked(slice: &[i32], index: usize) -> i32 {
    // SAFETY: the caller promises index < slice.len().
    unsafe { *slice.as_ptr().add(index) }
}

fn main() {
    let mut x = 5;
    let p: *mut i32 = &mut x;
    // SAFETY: p points at x, which is alive and not borrowed elsewhere.
    unsafe { *p += 1; }
    println!("{x}");

    let mut v = [1, 2, 3, 4, 5];
    let (a, b) = split_at_mut(&mut v, 2);
    a[0] = 10;
    b[0] = 30;                         // two &mut into one array, safely
    println!("{v:?}");

    // SAFETY: 4 < v.len()
    println!("{}", unsafe { get_unchecked(&v, 4) });

    let refused = std::panic::catch_unwind(|| {
        let mut w = [0; 2];
        split_at_mut(&mut w, 3);       // the assert stops it before any unsafe code
    });
    println!("{}", refused.is_err());
}
```

```output
6
[10, 2, 30, 4, 5]
5
true
```

`b[0]` is element 2 of `v`, which became 30. The call to `get_unchecked`
needed its own `unsafe` block at the call site, with a comment showing the
caller's side of the contract. The last call violated the precondition and
was stopped by the `assert!`, with a panic that `catch_unwind` caught (its
message goes to standard error), before any pointer was touched.

## Your turn

In `src/lib.rs`:

- `split_at_mut(slice, mid)`, as above: works for `mid` from 0 to `len`
  (including empty slices), and **panics** when `mid > len`
- `swap_unchecked(slice, a, b)`: an `unsafe fn` that swaps two elements
  through raw pointers (`std::ptr::swap`), with a `# Safety` section stating
  its contract. Swapping an element with itself (`a == b`) must work too;
  `ptr::swap` allows overlapping pointers.
- `Buffer`, a small growable byte buffer over a `Vec<u8>`:
  - `new()`: empty, with capacity **0**
  - `push(byte)`: when the buffer is full, grow the capacity to 8 if it was
    0, otherwise **double** it; so 5 pushes give capacity 8, and 9 pushes
    capacity 16. It never shrinks. `Vec::reserve_exact` asks for an exact
    amount.
  - `len()`, `is_empty()`, `capacity()`, and `as_bytes()` (a `&[u8]`)
  - `as_str() -> Option<&str>`: the bytes as text, checked with
    `std::str::from_utf8`; `None` if they are not valid UTF-8 (a single
    `0xff` byte, say)
  - `as_str_unchecked()`: an `unsafe fn` returning `&str` without checking,
    via `std::str::from_utf8_unchecked`, with a `# Safety` section
  - the tests also call `b.extend("héllo".bytes())`, so implement the
    standard `Extend<u8>` trait for `Buffer`: its one method,
    `fn extend<I: IntoIterator<Item = u8>>(&mut self, iter: I)`, pushes each
    byte
- every `unsafe {` block needs a comment containing `SAFETY:` (or the word
  `sound`): the tests read your source and require at least as many such
  comments as unsafe blocks
