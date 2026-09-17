---
title: FFI: calling C and being called
summary: extern "C", raw C strings, repr(C) structs, and wrapping an unsafe C API in a safe Rust one.
order: 7
files: [src/lib.rs]
run: cargo test
hints:
  - "Declare what you call: `unsafe extern \"C\" { fn strlen(s: *const c_char) -> usize; fn abs(n: c_int) -> c_int; }`. libc is linked already, so nothing else is needed."
  - "`c_strlen(s: &str)`: build a `CString::new(s)` (it fails on interior NUL bytes, hence the `Option`), then `unsafe { strlen(c.as_ptr()) }`."
  - "`from_c_string(ptr)` is an `unsafe fn`: `CStr::from_ptr(ptr).to_string_lossy().into_owned()`."
  - "`#[unsafe(no_mangle)] pub extern \"C\" fn learnbox_sum(ptr: *const i32, len: usize) -> i64` checks for null, then `slice::from_raw_parts(ptr, len).iter().map(|&x| x as i64).sum()`."
---

Rust talks to C directly: no runtime, no garbage collector, the same calling
conventions. That is how crates wrap `libsqlite3` or `libgit2`, and how Rust
code gets called from Python, Ruby or C.

## Calling a C function

```rust
use std::ffi::{c_char, c_int};

unsafe extern "C" {
    fn abs(n: c_int) -> c_int;
    fn strlen(s: *const c_char) -> usize;
}

let n = unsafe { abs(-3) };        // every call is unsafe: C has no guarantees
```

`extern "C"` sets the ABI. The `c_int`, `c_char`, `c_void`... aliases in
`std::ffi` match the platform's C types. libc is linked by default, so
`strlen`, `abs` and friends need no build script.

## Strings across the boundary

Rust strings are UTF-8 and know their length. C strings are NUL-terminated
bytes. The two never convert for free:

| Direction | Type | Notes |
|---|---|---|
| Rust to C, owned | `CString::new(s)?` | adds the NUL; fails if `s` contains one |
| Rust to C, borrowed | `c"literal"` | a `&CStr` literal |
| C to Rust, borrowed | `unsafe { CStr::from_ptr(p) }` | must be NUL-terminated and live long enough |
| C to Rust, owned | `.to_str()?` or `.to_string_lossy()` | UTF-8 is validated, not assumed |

Keep the `CString` alive while C holds the pointer. `CString::new(s).unwrap().as_ptr()`
in one expression is a classic use-after-free: the `CString` is dropped at the
end of the statement.

## Structs and repr(C)

Rust may reorder struct fields; C may not. Any struct crossing the boundary
needs `#[repr(C)]`:

```rust
#[repr(C)]
pub struct Point {
    pub x: f64,
    pub y: f64,
}
```

## Being called from C

```rust
#[unsafe(no_mangle)]
pub extern "C" fn learnbox_add(a: i32, b: i32) -> i32 {
    a + b
}
```

`no_mangle` keeps the symbol name; `extern "C"` sets the ABI. Two rules matter:

- **Never unwind into C.** A panic crossing the boundary is undefined behaviour;
  catch it with `std::panic::catch_unwind` in anything that might panic.
- **Validate everything.** Pointers may be null or unaligned; lengths may lie.
  Check what you can and document the rest in a `# Safety` section.

Build a `cdylib`/`staticlib` (in `Cargo.toml`, `[lib] crate-type = ["cdylib"]`)
and any language with a C FFI can load it. That is exactly how PyO3 makes Rust
callable from Python.

## The pattern: unsafe core, safe shell

The job of an FFI wrapper crate is to do all the checking once, so users never
write `unsafe`:

```rust
pub fn c_strlen(s: &str) -> Option<usize> {
    let owned = CString::new(s).ok()?;          // checked: no interior NUL
    Some(unsafe { strlen(owned.as_ptr()) })     // sound: owned lives to the end
}
```

## Your turn

In `src/lib.rs`:

- declare `strlen` and `abs` from libc and call them
- `c_strlen(s)`: length in bytes via C's `strlen`, `None` if `s` contains a NUL
- `c_abs(n)`: absolute value via C's `abs`
- `from_c_string(ptr)`: an `unsafe fn` turning a C string into a `String`,
  replacing invalid UTF-8
- `#[repr(C)] Point { x: f64, y: f64 }` and an `extern "C"` `learnbox_distance`
- `learnbox_sum(ptr, len)`: an `extern "C"` function summing an array from C;
  a null pointer or zero length gives 0, and it never panics across the boundary
