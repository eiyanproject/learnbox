---
title: Hello, cargo
summary: Create, build and run a Rust project, and meet functions, strings and format!.
order: 1
files: [src/lib.rs, src/main.rs]
run: cargo run
hints:
  - "`todo!()` compiles but panics when it runs. Replace it with an expression that produces a `String`."
  - "`format!` works like `println!` but returns the text: `format!(\"Hello, {name}!\")`."
  - "For `banner`, `\"=\".repeat(title.len())` makes the line. Join the three parts with `\\n` in one `format!`."
---

Rust programs are built with **cargo**, which compiles your code, fetches
libraries and runs tests. This workspace is already a cargo project:

```text
Cargo.toml        name, version, dependencies
src/lib.rs        a library: functions other code can use
src/main.rs       a binary: the program `cargo run` starts
```

Try these in the terminal:

```console
$ cargo build      # compile (the first build is the slowest)
$ cargo run        # compile if needed, then run src/main.rs
$ cargo check      # type-check without producing a binary: fastest feedback
```

Unlike Python, nothing runs until the whole program compiles. The compiler's
error messages are unusually helpful. Read them all the way through; they
often tell you the exact fix.

## Functions

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

- Every parameter has a type. The return type comes after `->`.
- The **last expression without a semicolon** is the return value. Adding a
  `;` turns it into a statement that returns nothing, and the compiler will
  complain that it expected `i32` and found `()`.
- `return x;` also exists, for leaving early.

`pub` makes a function visible outside its file. The tests (and `main.rs`)
live outside `lib.rs`, so everything they call must be `pub`.

## Printing and formatting

```rust
let name = "Ana";
let score = 92;
println!("{name} scored {score}");         // variables by name
println!("{} scored {}", name, score);     // or by position
let line = format!("{name}: {score:>5}");  // same syntax, returns a String
```

The `!` means these are **macros**, not functions: they are expanded at
compile time, which is how they check the format string against the values.

## Two kinds of string

- `&str` is a borrowed view of some text. String literals like `"hello"` are
  `&str`. Parameters that only read text usually take `&str`.
- `String` is text that owns its memory and can grow. `format!` returns one.

```rust
let s: String = String::from("hi");
let t: String = "hi".to_string();
let view: &str = &s;          // borrow a String as &str
```

The difference comes down to **ownership**, which gets its own lesson soon.

## todo!()

`todo!()` is a placeholder that satisfies the compiler and panics if it ever
runs. The starter uses it so the project compiles before you have written
anything.

## Your turn

In `src/lib.rs`:

- `greeting(name)` returns `"Hello, Ana!"` for `"Ana"`
- `banner(title)` returns the title between two lines of `=` as long as the
  title, joined with newlines: `banner("hi")` is `"==\nhi\n=="`

Then run `cargo run` to see `main.rs` use them, and press **Check**.
