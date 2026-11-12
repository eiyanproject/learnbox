---
title: "FFI: calling C and being called"
summary: extern "C", raw C strings, repr(C) structs, and wrapping an unsafe C API in a safe Rust one.
order: 7
files: [src/lib.rs]
run: cargo test
hints:
  - "Declare what you call: `unsafe extern \"C\" { fn strlen(s: *const c_char) -> usize; fn abs(n: c_int) -> c_int; }`. libc is linked already, so nothing else is needed."
  - "`c_strlen(s: &str)`: build a `CString::new(s)` (it fails on interior NUL bytes, hence the `Option`), then `unsafe { strlen(c.as_ptr()) }`."
  - "`from_c_string(ptr)` is an `unsafe fn`: return `String::new()` for a null pointer, otherwise `CStr::from_ptr(ptr).to_string_lossy().into_owned()`."
  - "`#[unsafe(no_mangle)] pub unsafe extern \"C\" fn learnbox_sum(ptr: *const i32, len: usize) -> i64` checks for null, then sums `slice::from_raw_parts(ptr, len)` inside `std::panic::catch_unwind`."
---

A huge amount of existing software is written in C, or exposes a C
interface: SQLite, OpenSSL, `libgit2`, the operating system itself. Most
other languages can call C, and be called by it. A **foreign function
interface** (FFI) is the mechanism for that, and Rust's is unusually direct:
there is no runtime or garbage collector to coordinate with, and Rust can use
C's calling conventions and memory layout exactly. That is how Rust crates
wrap C libraries, and how Rust code gets called from Python, Ruby or C.

Everything across the boundary is `unsafe` (lesson 1): C makes no promises
the Rust compiler can check. So FFI work follows one pattern throughout:
**an unsafe core, wrapped in a safe Rust API** that does all the checking
once, so users of your crate never write `unsafe` themselves.

## Calling a C function

To call a C function, declare its signature in an `extern "C"` block:

```rust
use std::ffi::{c_char, c_int};

unsafe extern "C" {
    fn abs(n: c_int) -> c_int;
    fn strlen(s: *const c_char) -> usize;
}

let n = unsafe { abs(-3) };        // every call is unsafe: C has no guarantees
```

(A fragment.) What each part means:

- `extern "C"` sets the **ABI** (application binary interface): how
  arguments are passed in registers and on the stack, so that Rust and C
  agree on how to call each other.
- The block is `unsafe extern` (required in the 2024 edition) because the
  compiler cannot check these declarations: if you get a signature wrong, the
  program misbehaves in ways nothing will report. You are promising the
  signatures match the C library.
- `c_int`, `c_char`, `c_long`, `c_void` and friends in `std::ffi` are the
  Rust types that match the platform's C types. `c_int` is `i32` on every
  common platform, but `c_long` differs between Linux and Windows, which is
  why the aliases exist.
- Calling one of these functions is `unsafe`, superpower 2 from lesson 1.

On Linux, Rust programs link against the C standard library (libc) already,
so `strlen`, `abs` and friends need no extra setup. A different C library
would be linked with a `#[link(name = "...")]` attribute or a build script.

## Strings across the boundary

The two languages represent text differently, and this is where most FFI
bugs live:

- a Rust `&str` is a pointer **and a length**, always UTF-8, and may contain
  a zero byte;
- a C string is just a pointer to bytes, ending at the first **NUL** (zero)
  byte, which is how C finds the end. There is no length, and no guarantee of
  any encoding.

So the two never convert for free, and `std::ffi` has a type for each side:

| Direction | Type | Notes |
|---|---|---|
| Rust to C, owned | `CString::new(s)` | copies `s` and adds the NUL; `Err` if `s` contains a NUL byte |
| Rust to C, literal | `c"text"` | a `&CStr` literal, NUL included |
| C to Rust, borrowed | `unsafe { CStr::from_ptr(p) }` | walks to the NUL; `p` must be a valid C string that lives long enough |
| C to Rust, owned | `cstr.to_str()` or `cstr.to_string_lossy()` | UTF-8 is checked, not assumed |

Why does `CString::new` fail on a NUL inside the text? Because C would read
`"bad\0inside"` as just `"bad"`, silently dropping the rest. That is why the
exercise's `c_strlen` returns an `Option`. And `to_string_lossy()` does not
fail at all: invalid UTF-8 bytes are replaced with `U+FFFD`, the `�`
replacement character, which is usually what you want for text coming from
C.

One classic bug deserves its own warning. `CString::as_ptr()` returns a
pointer into the `CString`'s buffer, so the `CString` must stay alive as long
as C uses the pointer:

```rust
let p = CString::new("hello").unwrap().as_ptr();   // the CString dies at the ;
unsafe { strlen(p) };                              // reads freed memory
```

```text
warning: this creates a dangling pointer because temporary `CString` is dropped at end of statement
  |
4 |     let p = CString::new("hello").unwrap().as_ptr();
  |             ------------------------------ ^^^^^^ pointer created here
  |             |
  |             this `CString` is dropped at end of statement
  |
  = help: bind the `CString` to a variable such that it outlives the pointer returned by `as_ptr`
```

The compiler now catches this common form, but only warns, and does not
catch every variant. The fix is to keep the `CString` in a variable for as
long as the pointer is in use.

## Structs and repr(C)

Rust may reorder a struct's fields (lesson 5); C never does. A struct that
crosses the boundary must have C's layout, which `#[repr(C)]` requests:

```rust
#[repr(C)]
pub struct Point {
    pub x: f64,
    pub y: f64,
}
```

Then a C `struct Point { double x; double y; }` and this Rust struct are the
same 16 bytes, and can be passed back and forth by value or by pointer.

## Being called from C

The other direction: making a Rust function callable from C.

```rust
#[unsafe(no_mangle)]
pub extern "C" fn learnbox_add(a: i32, b: i32) -> i32 {
    a + b
}
```

- `extern "C"` on a function definition gives it C's calling convention.
- `#[unsafe(no_mangle)]` keeps its symbol name exactly `learnbox_add`. By
  default, Rust **mangles** names, encoding the module path and a hash into
  the symbol, so two functions called `add` in different modules do not
  clash; C code looks symbols up by their plain name and would not find a
  mangled one. The attribute is written `unsafe(...)` in the 2024 edition,
  because two unmangled functions with the same name in one program are
  undefined behaviour. Prefix exported names (`learnbox_`) to avoid that.

Two rules matter for every exported function:

- **Never unwind into C.** If a Rust panic travels up into C code, which
  knows nothing about Rust panics, the behaviour is undefined. A function
  that might panic must catch it at the boundary with
  `std::panic::catch_unwind(|| { ... })`, which returns `Err` instead of
  unwinding, and turn that into an error value C understands (0, -1, a null
  pointer). Since Rust 1.81 an `extern "C"` function that panics aborts the
  program instead, which is safe but still a crash; catching is better.
- **Validate everything you can.** A pointer from C may be null; a length may
  be wrong. Check null and zero lengths in code, and write what you cannot
  check (that `ptr` really points at `len` values) in a `# Safety` section,
  marking the function `unsafe extern "C"` so Rust callers must use `unsafe`
  too.

To be loaded by another language, the crate is built as a C-compatible
library: `[lib] crate-type = ["cdylib"]` (a `.so` shared library) or
`"staticlib"` in `Cargo.toml`. Any language with a C FFI can then call it;
that is exactly how PyO3 makes Rust callable from Python.

## The pattern: unsafe core, safe shell

Every public function in an FFI wrapper crate does its checks, then makes one
small unsafe call, with a comment saying why it is sound:

```rust
pub fn c_strlen(s: &str) -> Option<usize> {
    let owned = CString::new(s).ok()?;          // checked: no interior NUL
    // SAFETY: owned is a valid NUL-terminated string, alive until the end of this function.
    Some(unsafe { strlen(owned.as_ptr()) })
}
```

Users of `c_strlen` get an ordinary safe function: no raw pointers, no
`unsafe`, no way to pass a string C would misread.

## Run it

```rust
use std::ffi::{c_char, c_int, CStr, CString};

unsafe extern "C" {
    fn abs(n: c_int) -> c_int;
    fn strlen(s: *const c_char) -> usize;
}

fn c_strlen(s: &str) -> Option<usize> {
    let owned = CString::new(s).ok()?;             // checked: no interior NUL
    Some(unsafe { strlen(owned.as_ptr()) })        // sound: owned lives to the end
}

#[allow(dead_code)]
#[repr(C)]
struct Point {
    x: f64,
    y: f64,
}

fn main() {
    println!("{}", unsafe { abs(-3) });
    println!("{:?} {:?}", c_strlen("héllo"), c_strlen("bad\0inside"));
    let lit: &CStr = c"from C";
    println!("{} {}", lit.to_str().unwrap(), lit.to_bytes_with_nul().len());
    println!("{}", std::mem::size_of::<Point>());
}
```

```output
3
Some(6) None
from C 7
16
```

C's `strlen` counts bytes, so `héllo` is 6, and a string with a NUL inside
cannot become a C string at all. The `c"from C"` literal is 6 characters
plus the NUL, 7 bytes. `Point` is the two `f64`s and nothing else.

## Your turn

In `src/lib.rs`:

- declare `strlen` and `abs` from libc in an `unsafe extern "C"` block
- `c_strlen(s)`: the length in bytes, computed by C's `strlen`; `None` if `s`
  contains a NUL byte
- `c_abs(n)`: the absolute value, computed by C's `abs`
- `from_c_string(ptr)`: an `unsafe fn` turning a C string into an owned
  `String`, replacing invalid UTF-8 with `�` (`to_string_lossy`). A **null**
  pointer gives `""`: the tests pass one, so check `ptr.is_null()` before
  calling `CStr::from_ptr`, which must never get null.
- `#[repr(C)] pub struct Point { pub x: f64, pub y: f64 }`, and an exported
  `extern "C"` function `learnbox_distance(a: Point, b: Point) -> f64`, the
  straight-line distance between them (√(dx² + dy²)); the tests call it
  without `unsafe`
- an exported `unsafe extern "C"` function
  `learnbox_sum(ptr: *const i32, len: usize) -> i64`, summing `len` values
  from C:
  - a null pointer or a length of 0 gives 0
  - the sum is an `i64`, so three `i32::MAX` values must not overflow
  - wrap the work in `std::panic::catch_unwind`, so it can never unwind into C
  - give it a `# Safety` section
- the tests read your source to check that it contains `no_mangle` and
  `catch_unwind`
