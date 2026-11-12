---
title: Designing a library API
summary: Builders, newtypes, sealed traits, must_use, accepting the widest input, and making misuse hard to compile.
order: 8
files: [src/lib.rs]
run: cargo test
hints:
  - "`ClientBuilder` takes `impl Into<String>` for the URL, and `build()` returns `Result<Client, BuildError>` so a missing URL is an error rather than a panic."
  - "`#[must_use]` on the `RequestBuilder` struct makes ignoring one a warning."
  - "Sealing: `mod private { pub trait Sealed {} }`, then `pub trait Backend: private::Sealed` and implement `Sealed` only for your own types, so outside crates cannot add implementations. For `describe`, give the trait a required `fn persistent(&self) -> bool` that the default method uses."
  - "`Timeout(Duration)` and `Retries(u8)` are newtypes, so `Client::configure(Timeout(..), Retries(..))` cannot be called with the arguments swapped."
---

Code that only you call can have any shape you like. The moment someone else
depends on it, including you in six months, its **API**, the set of public
types, functions and traits, matters more than its internals. Internals can
be rewritten on a quiet afternoon; changing a public signature breaks every
caller.

Good API design is mostly about the **call site**: is the right call easy to
write and to read, and is the wrong call hard to write at all? Rust has
specific tools for that, and this lesson collects them, mostly as
applications of things you already know: builders and `impl Into` (Advanced
lesson 6), newtypes (Advanced lesson 4), `#[must_use]`, and **sealed**
traits, which are new.

## Constructors and builders

A function with six parameters is unreadable at the call site:
`Client::new("https://api.example.com", 5, 3, true, None, false)`. Which
number is the timeout? What does `true` mean? A **builder** names each
setting, makes most of them optional with sensible defaults, and checks
everything at the end:

```rust
let client = Client::builder("https://api.example.com")
    .timeout(Duration::from_secs(5))
    .retries(3)
    .build()?;
```

(A fragment.) The pieces:

- `Client::builder(url)` takes only what is required, and returns a
  separate `ClientBuilder` holding the defaults.
- Each setter takes `self` **by value** and returns `Self`
  (`fn timeout(mut self, t: Duration) -> Self { self.timeout = t; self }`),
  so the calls chain, each one consuming the builder and handing back the
  updated one.
- `build()` validates and returns `Result<Client, BuildError>`. A library
  should not **panic** on input the caller could fix: return an error and
  let the caller decide. A precise error enum (Intermediate lesson 2) tells
  them what to fix.

## Accept the widest input, return the most specific type

Parameters should ask for the least they need, so callers do not have to
convert; return types should be specific, so callers can do the most with
them:

```rust
fn new(name: impl Into<String>) -> Self          // &str or String
fn open(path: impl AsRef<Path>) -> io::Result<File>
fn sum(values: &[i64]) -> i64                     // not &Vec<i64>
fn names(&self) -> impl Iterator<Item = &str>     // not a new Vec<String>
```

(Signatures.) `impl Into<String>` for a value you will **store** (only a
`&str` argument then costs an allocation), `AsRef` for one you only read
(Advanced lesson 6), slices instead of `&Vec`. Returning an iterator lets the
caller decide whether to collect, without the function allocating a `Vec`
they may not need.

## Newtypes stop argument mix-ups

Two parameters of the same type are easy to swap, and the compiler cannot
help:

```rust
fn configure(timeout_ms: u64, retries: u64)      // configure(3, 500) compiles, wrongly
```

Wrapping each in its own one-field struct, a **newtype**, makes the meaning
part of the type:

```rust
pub struct Timeout(pub Duration);
pub struct Retries(pub u8);

fn configure(t: Timeout, r: Retries)      // configure(Retries(3), Timeout(..)) will not compile
```

(Fragments.) The call site now says what each value is:
`client.configure(Timeout(Duration::from_millis(500)), Retries(2))`. A
newtype costs nothing at run time: it has exactly the layout of what it
wraps. The same trick gives validated values a type of their own: an `Email`
that was checked once, at the boundary, so that every function taking an
`Email` knows it is valid (Intermediate lesson 1's `Percent`).

## must_use

Some values do nothing until you use them. A `RequestBuilder` sends nothing
until `.send()`; forgetting that call is a silent bug. `#[must_use]` on a
type makes the compiler warn whenever a value of it is thrown away, with your
message:

```rust
#[must_use = "a RequestBuilder does nothing until you call send()"]
pub struct RequestBuilder { ... }
```

```text
warning: unused `RequestBuilder` that must be used
 --> src/lib.rs:4:14
  |
4 | pub fn f() { request(); }
  |              ^^^^^^^^^
  |
  = note: a RequestBuilder does nothing until you call send()
```

`Result` is already `#[must_use]`, which is why ignoring an error warns, and
so are iterator adapters (Beginner lesson 11's ``unused `Map` ``). It can also
go on a function, for a return value that must not be ignored. Add it
wherever ignoring the value is almost certainly a bug.

## Sealed traits

A public trait that anyone can implement is a promise. If you later add a
required method, every implementation in other people's crates stops
compiling, so you effectively cannot change the trait without a breaking
release. Sometimes, though, a trait only exists so that **your** types can
share an interface: storage backends that your crate provides, say. Then you
want users to *use* the trait, but not *implement* it. That is a **sealed**
trait:

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

How it works:

- `Backend` has a supertrait (Intermediate lesson 3), `private::Sealed`, so
  implementing `Backend` requires implementing `Sealed` first.
- `Sealed` is `pub`, so it may appear in a public trait's signature, but it
  lives in the **private** module `private`. Code outside your crate cannot
  name `private::Sealed`, so it cannot implement it, and therefore cannot
  implement `Backend`:

```text
error[E0603]: module `private` is private
   |
13 | impl storage::private::Sealed for Cloud {}
   |               ^^^^^^^  ------ trait `Sealed` is not publicly re-exported
   |               |
   |               private module
```

- Users can still call `Backend` methods and use `Box<dyn Backend>`; and
  you remain free to add methods to `Backend` later, since every
  implementation is in your own crate.

The standard library uses this for traits it may need to extend.

## The rest of the checklist

- Derive the obvious traits on public types: `Debug` always (users cannot
  add it themselves, the orphan rule), plus `Clone`, `PartialEq`, `Default`
  where they make sense.
- One error enum per crate (or per module), implementing `std::error::Error`.
- Document every public item; `#![deny(missing_docs)]` at the top of
  `lib.rs` makes a missing doc comment a compile error.
- Keep `pub` deliberate: re-export a small surface from `lib.rs` and keep the
  module layout private (Intermediate lesson 1).
- Follow the naming conventions: `as_` for cheap borrowed views (`as_str`),
  `to_` for conversions that cost something (`to_string`), `into_` for
  conversions that consume `self` (`into_bytes`); getters are named after
  the field (`url()`, not `get_url()`).

## Run it

```rust
use std::time::Duration;

#[derive(Debug)]
struct Client {
    url: String,
    timeout: Duration,
    retries: u8,
}

#[must_use = "a ClientBuilder does nothing until you call build()"]
struct ClientBuilder {
    url: String,
    timeout: Duration,
    retries: u8,
}

impl Client {
    fn builder(url: impl Into<String>) -> ClientBuilder {
        ClientBuilder { url: url.into(), timeout: Duration::from_secs(30), retries: 0 }
    }
}

impl ClientBuilder {
    fn timeout(mut self, t: Duration) -> Self {
        self.timeout = t;
        self
    }
    fn retries(mut self, n: u8) -> Self {
        self.retries = n;
        self
    }
    fn build(self) -> Result<Client, String> {
        if !self.url.starts_with("https://") {
            return Err(format!("not https: {}", self.url));
        }
        Ok(Client { url: self.url, timeout: self.timeout, retries: self.retries })
    }
}

fn main() {
    let client = Client::builder("https://api.example.com")
        .timeout(Duration::from_secs(5))
        .retries(3)
        .build();
    println!("{client:?}");
    println!("{:?}", Client::builder(String::from("http://x")).build().err());
}
```

```output
Ok(Client { url: "https://api.example.com", timeout: 5s, retries: 3 })
Some("not https: http://x")
```

`builder` took a `&str` the first time and a `String` the second:
`impl Into<String>` at work. The second builder failed validation, and the
caller got an `Err` to handle rather than a panic. (`Duration`'s `Debug`
prints `5s`.)

## Your turn

In `src/lib.rs`:

- `Client::builder(url)`, taking `impl Into<String>`, with chainable
  `.timeout(Duration)`, `.retries(u8)` and `.header(key, value)`, and
  `build() -> Result<Client, BuildError>`:
  - defaults: 30 seconds timeout, 0 retries, no headers
  - a URL that is empty or only whitespace is `BuildError::MissingUrl`
  - more than 10 retries is `BuildError::TooManyRetries(n)`; exactly 10 is
    fine
- getters on `Client`: `url()`, `timeout()`, `retries()`
- `Client::request(method, path)`, returning a `RequestBuilder` marked
  `#[must_use]`, with chainable `.header(key, value)` and `.send() -> String`
  (nothing is really sent; it describes the request):
  - the format is `"<METHOD> <url><path> [<k>: <v>, ...]"`, the client's
    headers first, then the request's, separated by `", "`:
    `"GET https://api.example.com/users [Authorization: Bearer t, Accept: json]"`,
    or `"POST https://api.example.com/x [Authorization: Bearer t]"`
  - the client URL may end with `/` and the path starts with `/`; join them
    with exactly one (`"https://api.example.com/"` plus `"/users"` is
    `"https://api.example.com/users"`)
- newtypes `Timeout(pub Duration)` and `Retries(pub u8)`, and
  `Client::configure(&mut self, Timeout, Retries)` that sets both
- a **sealed** trait `Backend`, implemented for two types of your own:
  - `Memory`, a unit struct, named `"memory"`, not persistent
  - `Disk { path: String }`, deriving `Default`, named `"disk"`, persistent
  - required methods `name(&self) -> &str` and a way to say whether it is
    persistent; a **default** method `describe(&self) -> String` giving
    `"memory (volatile)"` and `"disk (persistent)"`
  - it must work as `Box<dyn Backend>`
- the tests read your source for `#[must_use`, `Sealed` and
  `impl Into<String>`
