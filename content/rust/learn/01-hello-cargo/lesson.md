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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **compiled language** | the whole program is translated into a native program before anything runs |
| **compiler** (`rustc`) | the program that does that translation |
| **cargo** | Rust's build tool and package manager; it runs the compiler, fetches libraries and runs tests |
| **crate** | a Rust package: a library or a program |
| **library crate** | code for other code to call: `src/lib.rs` |
| **binary crate** | a program you can run: `src/main.rs` |
| **`Cargo.toml`** | the project's name, version and dependencies |
| **dependency** | a library your project uses |
| **type-check** | confirm the types fit, without producing a program |
| **error code** | the `E0308` in `error[E0308]`, which `rustc --explain` describes |
| **`-->`** | in an error, the file, line and column |
| **`^^^`**, **`---`** | in an error, the exact spot; something related |
| **`help:`** | the compiler's suggested fix |
| **function** | a named block of code, declared with `fn` |
| **parameter** | a named input with its type: `a: i32` |
| **return type** | the type after `->` |
| **expression** | code that produces a value: `a + b` |
| **statement** | code that does something and produces nothing: `a + b;`, `let x = 5;` |
| **tail expression** | the last expression of a block, with no semicolon: the block's value |
| **unit** (`()`) | the type of "no value" |
| **`pub`** | public: visible outside its file |
| **macro** | code expanded at compile time, called with `!`: `println!` |
| **format string** | text with `{}` placeholders, checked by the compiler |
| **format specification** | after a colon in `{}`: `{score:>5}` right-aligns in 5 characters |
| **`&str`** | a borrowed view of text; string literals are `&str` |
| **`String`** | text that owns its memory and can grow |
| **ownership** | who is responsible for a value's memory (Learn lesson 4) |
| **panic** | the program stops with an error message |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo build` | compiles the project |
| `cargo run` | compiles if needed, then runs `src/main.rs` |
| `cargo check` | type-checks without producing a program: the fastest feedback |
| `cargo test` | compiles and runs the tests |
| `rustc --explain E0308` | a long explanation of an error code, with examples |
| `$` | stands for the prompt: do not type it |

### Rust keywords, functions and macros

| Name | What it does |
|---|---|
| `pub fn add(a: i32, b: i32) -> i32 { a + b }` | a public function returning the sum |
| `return x;` | leaves the function early with `x` |
| `i32` | a 32-bit signed whole number |
| `println!("{name} scored {}", score)` | prints with placeholders and a line break |
| `format!(...)` | builds the same text and returns a `String` |
| `"=".repeat(n)` | the text repeated `n` times |
| `title.len()` | the length in bytes |
| `"\n"` | a line break inside a string |
| `todo!()` | a placeholder that compiles and panics if it runs |

### Errors

| Error | Means |
|---|---|
| `error[E0308]: mismatched types` ... `expected i32, found ()` | a stray semicolon turned the return value into a statement |
| `function greeting is private` | it needs `pub` to be used from outside |
| a typo such as `{nmae}` | a compile error, because format strings are checked |

---

Rust is a **compiled** language: a program called the compiler, `rustc`,
translates your source code into a native program before anything runs. You
rarely call `rustc` yourself. Rust projects are built with **cargo**, the
build tool and package manager, which runs the compiler for you, fetches
libraries (Rust calls them **crates**) and runs tests. This workspace is
already a cargo project:

```text
Cargo.toml        name, version, dependencies
src/lib.rs        a library: functions other code can use
src/main.rs       a binary: the program `cargo run` starts
```

A **library** crate is code for other code to call; a **binary** crate is a
program you can run. This project has both: `main.rs` is a small program
that calls the functions in `lib.rs`, and the tests call them too.

Try these in the terminal (type each command without the `$`, which stands
for the prompt):

```console
$ cargo build      # compile (the first build is the slowest)
$ cargo run        # compile if needed, then run src/main.rs
$ cargo check      # type-check without producing a binary: fastest feedback
```

Unlike Python, nothing runs until the whole program compiles. That sounds
like a burden, and it is the main thing Rust gives you: whole classes of bug
are caught before the program ever starts.

### Reading a compiler error

The compiler's error messages are unusually helpful: they point at the exact
spot, explain the problem, and often suggest the fix. Here is a function with
one stray character, a semicolon after its last line:

```rust
pub fn add(a: i32, b: i32) -> i32 {
    a + b;
}
```

`cargo check` says:

```text
error[E0308]: mismatched types
 --> src/lib.rs:1:31
  |
1 | pub fn add(a: i32, b: i32) -> i32 {
  |        ---                    ^^^ expected `i32`, found `()`
  |        |
  |        implicitly returns `()` as its body has no tail or `return` expression
2 |     a + b;
  |          - help: remove this semicolon to return this value
```

How to read it, from the top:

1. **The first line** names the problem, `mismatched types`, with an error
   code, `E0308`.
2. **`-->`** gives the file, line and column: `src/lib.rs`, line 1, column 31.
3. **The lines with `|`** quote your code. `^^^` marks the spot the error is
   about, and `---` marks something related, each with a short explanation.
4. **`help:`** suggests a fix, and here it is exactly right: remove the
   semicolon (the Functions section below explains why).

For a longer explanation of any error code, with examples, run
`rustc --explain E0308`. When a message is long, read the first line and the
`help:` first; they usually hold the key. Read errors all the way through
like this, and you will find many of them tell you the exact fix.

## Functions

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

Piece by piece:

- `fn` starts a function, then its name, `add`.
- Every parameter has a type, written after a colon: `a: i32` is a 32-bit
  signed whole number. The return type comes after `->`.
- The **last expression without a semicolon** is the return value. Adding a
  `;` turns it into a statement that returns nothing, and the compiler will
  complain that it expected `i32` and found `()`, the error above.
- `return x;` also exists, for leaving early.

That last rule is Rust's distinction between an **expression**, which
produces a value (`a + b`), and a **statement**, which does something and
produces nothing (`a + b;`, or `let x = 5;`). The semicolon turns an
expression into a statement. `()`, said "unit", is the type of "no value",
which is what a statement gives you.

`pub` (public) makes a function visible outside its file. The tests (and
`main.rs`) live outside `lib.rs`, so everything they call must be `pub`.
Without it, a test calling `greeting` fails to compile with
`function greeting is private`.

## Printing and formatting

```rust
let name = "Ana";
let score = 92;
println!("{name} scored {score}");         // variables by name
println!("{} scored {}", name, score);     // or by position
let line = format!("{name}: {score:>5}");  // same syntax, returns a String
```

(A fragment.) `{name}` inside the string is replaced by the variable
`name`'s value; `{}` takes the next argument after the string instead.
After a colon comes a **format specification**: `{score:>5}` right-aligns
the value in 5 characters.

The `!` means these are **macros**, not functions: they are expanded at
compile time, which is how they check the format string against the values.
A typo such as `{nmae}` is a compile error, not a surprise at run time.
`println!` prints the text and a line break; `format!` builds the same text
and returns it as a `String` instead of printing it.

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

## Run it

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn main() {
    let name = "Ana";
    let score = 92;
    println!("{name} scored {score}");
    println!("{} scored {}", name, score);
    let line = format!("{name}: {score:>5}|");   // the | shows the padding
    println!("{line}");
    println!("{}", add(2, 3));
}
```

```output
Ana scored 92
Ana scored 92
Ana:    92|
5
```

## Your turn

In `src/lib.rs`:

- `greeting(name)` returns `"Hello, Ana!"` for `"Ana"`, as a `String`
- `banner(title)` returns the title between two lines of `=` as long as the
  title, joined with newlines: `banner("hi")` is `"==\nhi\n=="` (`\n` is a
  line break inside a string), and `banner("learnbox")` has eight `=` on each
  line

Then run `cargo run` to see `main.rs` use them, and press **Check**.
