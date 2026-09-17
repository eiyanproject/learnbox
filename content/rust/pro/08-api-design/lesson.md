---
title: Designing a library API
summary: Builders, newtypes, sealed traits, must_use, accepting the widest input, and making misuse hard to compile.
order: 8
files: [src/lib.rs]
run: cargo test
hints:
  - "`ClientBuilder` takes `impl Into<String>` for the URL, keeps `Option` fields, and `build()` returns `Result<Client, BuildError>` so a missing URL is an error rather than a panic."
  - "`#[must_use]` on `Client::request` makes ignoring the returned `RequestBuilder` a warning; on `BuildError` it stops silent discards."
  - "Sealing: `mod private { pub trait Sealed {} }`, then `pub trait Backend: private::Sealed` and implement `Sealed` only for your own types, so outside crates cannot add implementations."
  - "`Timeout(Duration)` and `Retries(u8)` are newtypes, so `Client::configure(Timeout(..), Retries(..))` cannot be called with the arguments swapped."
---

Once code is used by someone else (including you in six months), the shape of
its API matters more than its internals. Rust has specific tools for making the
right call easy and the wrong call impossible.

## Constructors and builders

A function with six parameters is unreadable at the call site. A **builder**
names each one, makes most optional, and can validate at the end:

```rust
let client = Client::builder("https://api.example.com")
    .timeout(Duration::from_secs(5))
    .retries(3)
    .build()?;
```

Take `self` by value and return `Self` so calls chain. Validate in `build()`
and return a `Result`: a library should not panic on bad input a caller can fix.

## Accept the widest input, return the most specific type

```rust
fn new(name: impl Into<String>) -> Self          // &str or String
fn open(path: impl AsRef<Path>) -> io::Result<File>
fn sum(values: &[i64]) -> i64                     // not &Vec<i64>
fn names(&self) -> impl Iterator<Item = &str>     // not Vec<String>
```

## Newtypes stop argument mix-ups

```rust
pub struct Timeout(pub Duration);
pub struct Retries(pub u8);

fn configure(t: Timeout, r: Retries)      // configure(Retries(3), Timeout(..)) will not compile
```

The same trick gives validated values a type of their own: a `Percent` that
cannot be 150, an `Email` that was checked once at the boundary.

## must_use

```rust
#[must_use = "a RequestBuilder does nothing until you call send()"]
pub struct RequestBuilder { ... }
```

`Result` is already `#[must_use]`; add it to types and methods where ignoring
the value is a bug.

## Sealed traits

A public trait anyone can implement is a commitment: adding a method breaks
their code. If the trait exists only to enumerate **your** types, seal it:

```rust
mod private {
    pub trait Sealed {}
}

pub trait Backend: private::Sealed {
    fn name(&self) -> &str;
}

impl private::Sealed for Memory {}
impl Backend for Memory { ... }
```

Outside crates cannot name `private::Sealed`, so they cannot implement `Backend`,
and you stay free to extend it.

## The rest of the checklist

- Derive the obvious traits: `Debug` on everything public, plus `Clone`,
  `PartialEq`, `Default` where they make sense.
- One error enum per crate, implementing `Error` (see Intermediate: errors).
- Document every public item; `#[deny(missing_docs)]` keeps it honest.
- Keep `pub` deliberate: re-export a small surface from `lib.rs` and keep the
  module layout private (Intermediate: modules).
- Follow the naming conventions: `as_` borrows cheaply, `to_` converts at a
  cost, `into_` consumes.

## Your turn

In `src/lib.rs`:

- `Client::builder(url)` accepting `&str` or `String`, with `.timeout(..)`,
  `.retries(..)`, `.header(k, v)` and `build() -> Result<Client, BuildError>`;
  an empty URL is `BuildError::MissingUrl`, more than 10 retries is
  `BuildError::TooManyRetries(n)`. Defaults: 30 s timeout, 0 retries.
- `Client::request(method, path)` returning a `#[must_use]` `RequestBuilder`
  with `.header(k, v)` and `.send()` producing
  `"GET https://api.example.com/users [Accept: json]"` (client headers first, then request headers)
- `Timeout` and `Retries` newtypes, and `Client::configure(Timeout, Retries)`
- a **sealed** `Backend` trait implemented for `Memory` and `Disk`, with
  `describe(&self)` provided by the trait
