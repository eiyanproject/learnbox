---
title: Designing errors
summary: A custom error enum with Display and std::error::Error, From conversions so ? converts errors for you, source chains, and Box<dyn Error> at the top.
order: 2
files: [src/lib.rs]
run: cargo test
hints:
  - "`ConfigError` has variants `Missing(String)`, `InvalidNumber { key: String, source: ParseIntError }` and `OutOfRange { key: String, value: i64 }`, with `#[derive(Debug)]`."
  - "`impl fmt::Display for ConfigError`: one `match self` arm per variant, using `write!(f, ...)` with the exact messages from the lesson."
  - "`impl std::error::Error for ConfigError { fn source(&self) -> Option<&(dyn Error + 'static)> { match self { Self::InvalidNumber { source, .. } => Some(source), _ => None } } }`."
  - "`get_port`: `let raw = config.get(\"port\").ok_or_else(|| ConfigError::Missing(\"port\".into()))?;` then `raw.trim().parse::<i64>().map_err(|source| ConfigError::InvalidNumber { key: \"port\".into(), source })?`, then the range check."
---

The Beginner track used `Result<T, String>` for errors. A string is fine for
a quick program, but think about the **caller** of a function that loads a
configuration and returns `Err("port out of range: 70000")`. To react
differently to "the key is missing" (use a default) and "the value is
broken" (stop and complain), the caller would have to inspect the text, and
the day you reword a message, their code silently breaks.

The fix is to make each kind of failure a value the caller can `match` on:
an error **type**, usually an enum, with one variant per thing that can go
wrong. This lesson builds one, step by step, and connects it to the
standard library's error machinery, so that `?` and printing work as
expected.

## An error enum

```rust
use std::num::ParseIntError;

#[derive(Debug)]
pub enum LoadError {
    NotFound(String),
    BadNumber { line: usize, source: ParseIntError },
}
```

(A fragment.) Each variant is one way to fail, carrying the data a caller
needs to react or to report it: *which* file was not found, *which* line had
the bad number, and the original `ParseIntError` that says what was wrong
with it. A caller can now write `match err { LoadError::NotFound(_) => ...,
... }`, and if you add a variant later, every exhaustive `match` points out
the new case (lesson 7).

`#[derive(Debug)]` is not optional here: the `Error` trait below requires it,
and `unwrap()` uses it to print the error when it panics.

## Display: the message for people

An error type should print a message meant for a human, with `{}`. That is
the `Display` trait (lesson 10), with one `match` arm per variant:

```rust
use std::fmt;

impl fmt::Display for LoadError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            LoadError::NotFound(path) => write!(f, "file not found: {path}"),
            LoadError::BadNumber { line, .. } => write!(f, "bad number on line {line}"),
        }
    }
}
```

`{ line, .. }` binds the `line` field and ignores the rest: `..` in a struct
pattern means "and any other fields". Conventionally the message is short,
lower-case and without a full stop, because it often ends up inside a
longer one: `error: bad number on line 3`.

The two kinds of printing have different readers: `{}` (Display) is for the
user of the program, `{:?}` (Debug) for the programmer, showing the variant
and every field: `BadNumber { line: 3, source: ParseIntError { kind:
InvalidDigit } }`.

## The Error trait, and source chains

`std::error::Error` is the standard library's trait for "this is an error".
Implementing it is what lets your type work with everything else that
handles errors, such as `Box<dyn Error>` below. It needs `Debug` and
`Display` first; forget `Display` and the compiler says so:

```text
error[E0277]: `LoadError` doesn't implement `std::fmt::Display`
 --> src/lib.rs:3:28
  |
3 | impl std::error::Error for LoadError {}
  |                            ^^^^^^^^^ unsatisfied trait bound
```

All of its methods have defaults, so `impl std::error::Error for LoadError {}`
with an empty body is a complete implementation. The one worth writing is
`source()`:

```rust
impl std::error::Error for LoadError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            LoadError::BadNumber { source, .. } => Some(source),
            _ => None,
        }
    }
}
```

`source()` answers "what lower-level error caused this one?". Errors come in
layers: the program could not load its settings, *because* line 3 of the
file had a bad number, *because* `"4x"` has an invalid digit. Each layer's
message is meaningful on its own, and `source()` links each to the next,
forming a **source chain**:

```text
LoadError::BadNumber        "bad number on line 3"
   └── source(): ParseIntError   "invalid digit found in string"
          └── source(): None
```

The return type reads: "maybe (`Option`) a reference (`&`) to some error
type (`dyn Error`, decided at run time) that contains no short-lived
borrows (`'static`)". `NotFound` has no underlying cause, so it returns
`None`. A good rule: either put the cause in your `Display` message, or
return it from `source()`, but not both, or a printed chain shows the same
text twice. `LoadError` returns it from `source()`.

## From: making ? convert for you

Lesson 8 showed that `?` on an `Err(e)` returns `Err(From::from(e))`: it
converts the error into the function's error type, if a conversion exists.
Implement `From` for your type, and lower-level errors convert silently:

```rust
#[derive(Debug)]
enum AppError {
    Io(std::io::Error),
}

impl From<std::io::Error> for AppError {
    fn from(e: std::io::Error) -> Self {
        AppError::Io(e)
    }
}

fn read_config() -> Result<String, AppError> {
    let text = std::fs::read_to_string("app.toml")?;   // io::Error becomes AppError::Io
    Ok(text)
}
```

(A fragment.) `read_to_string` returns `Result<String, io::Error>`, and
`read_config` returns `Result<String, AppError>`. Without the `From` impl,
the `?` would fail with lesson 8's ``?` couldn't convert the error`` message.
With it, `?` calls `AppError::from(e)` on the way out.

`From` only sees the lower-level error. When the new error needs context the
old one does not have (which key? which line?), convert by hand with
`map_err`, a closure that builds the new error from the old one:

```rust
text.trim().parse().map_err(|source| LoadError::BadNumber { line, source })
```

(An expression.) `|source| ...` receives the `ParseIntError`, and the struct
literal uses field init shorthand (Beginner lesson 6) for both `line`, from
the surrounding function, and `source`. The exercise uses exactly this
pattern. Its cousin `ok_or_else` turns an `Option` into a `Result`, calling
a closure for the error when the value is `None`:
`map.get("port").ok_or_else(|| ConfigError::Missing("port".into()))?`.

## Box<dyn Error>: the application boundary

A precise error enum is right for a library, where callers need to react to
each case. At the top of an application, in `main`, there is usually only
one reaction: print the message and stop. Listing every possible error type
there would be tiresome. `Box<dyn Error>` means "some error, of any type
that implements `Error`", boxed because the types differ in size (the
`Box<dyn Trait>` of Beginner lesson 10):

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let config = load_file("app.toml")?;   // a LoadError, say
    let port = get_port(&config)?;         // a ConfigError
    Ok(())
}
```

(A fragment.) Both `?`s work because the standard library implements `From`
for `Box<dyn Error>` from every type that implements `Error`: each error is
boxed on the way out. When `main` returns an `Err`, Rust prints it in debug
form and exits with a failure status.

The box forgets the concrete type, but it can be asked: `err.downcast_ref::
<ConfigError>()` returns `Some(&ConfigError)` if the boxed error is a
`ConfigError`, otherwise `None`. The exercise's tests use this to check
that `load` really passes your error through.

A rule of thumb: **libraries return precise enums; `main` and top-level glue
use `Box<dyn Error>`**. Two popular crates automate these styles: `thiserror`
derives the `Display`, `Error` and `From` impls of this lesson, and `anyhow`
provides a better `Box<dyn Error>`. Knowing what they generate makes both
straightforward to use.

## Run it

```rust
use std::error::Error;
use std::fmt;
use std::num::ParseIntError;

#[derive(Debug)]
enum LoadError {
    NotFound(String),
    BadNumber { line: usize, source: ParseIntError },
}

impl fmt::Display for LoadError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            LoadError::NotFound(path) => write!(f, "file not found: {path}"),
            LoadError::BadNumber { line, .. } => write!(f, "bad number on line {line}"),
        }
    }
}

impl Error for LoadError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            LoadError::BadNumber { source, .. } => Some(source),
            _ => None,
        }
    }
}

fn parse_line(line: usize, text: &str) -> Result<i32, LoadError> {
    text.trim().parse().map_err(|source| LoadError::BadNumber { line, source })
}

fn main() {
    let e = parse_line(3, "4x").unwrap_err();
    println!("{e}");
    let mut cause = e.source();
    while let Some(c) = cause {
        println!("caused by: {c}");
        cause = c.source();
    }
    println!("{e:?}");
    println!("{}", LoadError::NotFound("app.toml".into()));
    let boxed: Box<dyn Error> = Box::new(e);       // any Error fits the box
    println!("{boxed} / {}", boxed.downcast_ref::<LoadError>().is_some());
    println!("{:?}", parse_line(1, " 7 ").ok());
}
```

```output
bad number on line 3
caused by: invalid digit found in string
BadNumber { line: 3, source: ParseIntError { kind: InvalidDigit } }
file not found: app.toml
bad number on line 3 / true
Some(7)
```

The `while let` loop walks the source chain: one cause, then `source()` of
the `ParseIntError` is `None` and the loop ends. Debug shows every field;
Display only the message. After boxing, the message is unchanged, and
`downcast_ref` recovers the concrete type.

## Your turn

In `src/lib.rs`, configuration arrives as a `HashMap<String, String>` of key
to raw text.

- `ConfigError`, deriving `Debug`, with exactly these variants:
  `Missing(String)`, `InvalidNumber { key: String, source: ParseIntError }`
  and `OutOfRange { key: String, value: i64 }`
- `Display`, using the key's name in each message (the tests use both
  `port` and `workers`):
  - `Missing` prints `missing key: port`
  - `InvalidNumber` prints `port is not a number` (the cause goes in
    `source()`, not in the message)
  - `OutOfRange` prints `port out of range: 70000`
- `Error`, with `source()` returning the `ParseIntError` for `InvalidNumber`
  and `None` for the other two
- `get_port(config)`: the `"port"` value as a `u16` from 1 to 65535, with
  whitespace around it ignored (`" 8080 "` is 8080). A missing key is
  `Missing("port")`. Text that is not a whole number is `InvalidNumber`.
  Numbers outside the range, **including negative ones**, are `OutOfRange`
  with the parsed value: `"0"`, `"70000"` and `"-1"` give values 0, 70000 and
  -1. So parse into `i64` first, then check the range, then convert.
- `get_workers(config)`: the `"workers"` value, `Ok(4)` when the key is
  missing; otherwise the same rules with the range 1 to 64
- `load(config)`: both, as `Ok((port, workers))`, returning
  `Result<(u16, u16), Box<dyn Error>>` and using `?` on each

`get_port` and `get_workers` differ only in key and range. A private helper
such as `fn parse_in_range(key: &str, raw: &str, min: i64, max: i64) ->
Result<u16, ConfigError>` saves writing the logic twice.
