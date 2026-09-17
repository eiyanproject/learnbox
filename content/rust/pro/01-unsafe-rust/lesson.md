---
title: Unsafe Rust
summary: Raw pointers, what unsafe actually permits, and wrapping it in a safe API whose invariants you can state.
order: 1
files: [src/lib.rs]
run: cargo test
hints:
  - "`split_at_mut`: `let len = slice.len(); let ptr = slice.as_mut_ptr(); assert!(mid <= len);` then in one `unsafe` block return `(slice::from_raw_parts_mut(ptr, mid), slice::from_raw_parts_mut(ptr.add(mid), len - mid))`."
  - "`swap_unchecked` is an `unsafe fn`: document the contract (`a` and `b` must be in bounds) and use `std::ptr::swap(ptr.add(a), ptr.add(b))`."
  - "`Buffer::push` grows by doubling: allocate a new `Vec<u8>` with `Vec::with_capacity`, copy, and keep the length. Keep the unsafe part tiny; everything else is safe code."
  - "`as_str` is safe only if the bytes really are UTF-8, so validate with `std::str::from_utf8` and return `Option<&str>`. `as_str_unchecked` is the `unsafe fn` version using `from_utf8_unchecked`."
---

Safe Rust guarantees no data races, no use-after-free, no dangling references.
Some things the compiler cannot prove are still correct: splitting a slice into
two mutable halves, talking to C, implementing `Vec`. `unsafe` is how you say
"I have checked this myself".

## What unsafe actually allows

Inside an `unsafe` block you gain exactly five powers:

1. dereference a raw pointer (`*const T`, `*mut T`)
2. call an `unsafe fn` (including `extern "C"` functions)
3. implement an `unsafe trait` (`Send`, `Sync`)
4. access or modify a `static mut`
5. access fields of a `union`

Everything else keeps its usual rules. `unsafe` does **not** turn off the
borrow checker; it is not "C mode". Most of the code inside an `unsafe` block
is ordinary Rust.

## Raw pointers

```rust
let mut x = 5;
let p: *mut i32 = &mut x;
unsafe { *p += 1; }
```

Raw pointers may be null, dangling, unaligned, and may alias each other. The
compiler will not check any of it, and breaking the rules is **undefined
behaviour**: not a panic, but a program that may do anything, including working
until it does not.

The rules you are promising to keep:

- the pointer is non-null, aligned, and points at a live, initialised value
- no `&mut` overlaps with any other reference to the same data
- data is valid for its type (a `bool` is 0 or 1; a `&T` is never null; a `str` is UTF-8)

## Safe wrappers

The point of `unsafe` is to be **contained**. Write the smallest possible
unsafe core, check the preconditions yourself, and expose a safe function:

```rust
pub fn split_at_mut(slice: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    let len = slice.len();
    let ptr = slice.as_mut_ptr();
    assert!(mid <= len);                                  // the invariant, checked
    unsafe {
        (
            std::slice::from_raw_parts_mut(ptr, mid),
            std::slice::from_raw_parts_mut(ptr.add(mid), len - mid),
        )
    }
}
```

Callers cannot misuse this: the `assert!` makes the unsafe part sound. That is
exactly how the standard library's own `split_at_mut` works.

## Unsafe functions

If a function cannot check its own preconditions, make it `unsafe fn` and
document them in a `# Safety` section. Then the caller must write `unsafe`, and
the contract is visible:

```rust
/// # Safety
/// `index` must be less than `slice.len()`.
pub unsafe fn get_unchecked(slice: &[i32], index: usize) -> i32 {
    unsafe { *slice.as_ptr().add(index) }
}
```

## Rules of thumb

- Reach for `unsafe` only when safe Rust genuinely cannot express it, or when a
  measured hot spot needs it. `split_at_mut`, `Cell`, `Vec` and FFI are the
  classic reasons.
- Every `unsafe` block gets a comment saying **why it is sound**.
- Test under Miri (`cargo +nightly miri test`) when you can: it catches many
  kinds of undefined behaviour that normal tests miss.

## Your turn

In `src/lib.rs`:

- `split_at_mut(slice, mid)`: as above, panicking when `mid > len`
- `swap_unchecked(slice, a, b)`: an `unsafe fn` with a `# Safety` section,
  swapping two elements by raw pointer
- `Buffer`: a tiny growable byte buffer with `new`, `push`, `len`, `capacity`,
  `as_bytes`, `as_str` (validated, `Option<&str>`) and
  `as_str_unchecked` (an `unsafe fn`). Capacity doubles from 8 and never shrinks.
- every `unsafe` block carries a comment explaining why it is sound
