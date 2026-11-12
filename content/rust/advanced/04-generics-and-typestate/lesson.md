---
title: Generics and typestate
summary: where clauses, associated constants, PhantomData, and encoding a state machine in types so invalid calls do not compile.
order: 4
files: [src/lib.rs]
run: cargo test
hints:
  - "`Shape` has `const SIDES: u32;` and `fn name() -> &'static str`. `total_sides<A: Shape, B: Shape>() -> u32 { A::SIDES + B::SIDES }` needs no values at all."
  - "`Request<State>` holds the data plus `_state: PhantomData<State>`. `impl Request<Empty> { pub fn url(self, url: &str) -> Request<HasUrl> { ... } }` consumes the old builder and returns one in the next state."
  - "Only `impl Request<HasUrl>` gets `header(...)` and `send()`, so `Request::new().send()` does not compile."
  - "`largest_by<T, K, F>(items: &[T], key: F) -> Option<&T> where F: Fn(&T) -> K, K: PartialOrd`: loop, keeping the best item and its key."
---

So far, types have described what data *is*: an `f64`, a `Vec<String>`. This
lesson uses them to describe what data *means*, and what may be done with it
right now. The goal is the most useful trick in Rust API design: turning a
rule that would be a run-time check ("you must set the URL before sending")
into one the compiler enforces, so breaking it does not compile at all.

It takes four tools, each small on its own: `where` clauses for readable
bounds, **associated constants** on traits, **`PhantomData`** for types that
exist only to tag a value, and **typestate**, which combines them.

## where clauses

When a function has several type parameters with long bounds, the signature
becomes hard to read. A `where` clause moves the bounds after it:

```rust
fn summarize<T, K, F>(items: &[T], key: F) -> Vec<K>
where
    F: Fn(&T) -> K,
    K: Ord + Clone,
{ ... }
```

(A signature.) It means exactly the same as
`fn summarize<T, K, F: Fn(&T) -> K, K: Ord + Clone>(...)`, but reads as
"for item type `T`, key type `K` and key function `F`, where `F` turns a
`&T` into a `K` and `K` can be sorted". `where` can also express bounds the
inline form cannot, such as bounds on a type that is not a parameter
(`where Vec<T>: Debug`).

## Associated constants

A trait can require each implementing type to provide a **constant**, much
as it requires methods:

```rust
trait Unit {
    const SYMBOL: &'static str;
    const PER_METER: f64;
}

struct Km;
impl Unit for Km {
    const SYMBOL: &'static str = "km";
    const PER_METER: f64 = 0.001;
}

fn label<U: Unit>(meters: f64) -> String {
    format!("{} {}", meters * U::PER_METER, U::SYMBOL)
}

label::<Km>(1500.0)     // "1.5 km"
```

(A fragment.) Two new things here:

- The constants belong to the **type**, not to a value: `U::PER_METER` is
  read from the type parameter, and `label` never receives a `Km` value at
  all. `Km` is a struct with no fields, used only as a name for the type.
- Because no argument mentions `U`, the compiler cannot work it out, so the
  caller names it with the turbofish: `label::<Km>(...)`. Without it:
  ``error[E0283]: type annotations needed``.

Functions without `self` work the same way: a trait method
`fn name() -> &'static str` is called as `Km::name()`, or, when the
compiler needs to be told which trait it comes from,
`<Km as Unit>::name()`. The constant is fixed when the program is compiled,
so there is no cost at run time.

## PhantomData

Here is a mix-up types could catch. Users and orders both have numeric ids,
so a function `find_user(id: u64)` happily accepts an order id. A separate
struct for each kind of id works but repeats code. A generic `Id<T>`,
where `T` says which kind, would be ideal, but:

```rust
pub struct Id<T> {
    value: u64,
}
```

```text
error[E0392]: type parameter `T` is never used
 --> src/lib.rs:1:15
  |
1 | pub struct Id<T> {
  |               ^ unused type parameter
  |
  = help: consider removing `T`, referring to it in a field, or using a marker such as `PhantomData`
```

The compiler insists every type parameter is used by some field. (It works
out how `Id<T>` may be converted between different `T`s, a property called
**variance**, from how the fields use `T`, and with no such field it would be
guessing.) The `help:` names the answer: `std::marker::PhantomData<T>`, a field
type that **acts as if** it held a `T`, while holding nothing:

```rust
use std::marker::PhantomData;

struct Id<T> {
    value: u64,
    _kind: PhantomData<T>,
}

type UserId = Id<User>;
type OrderId = Id<Order>;      // a different type from UserId
```

(A fragment.) `PhantomData` is **zero-sized**: it takes no memory, so an
`Id<User>` is exactly as big as a `u64`, and copying one costs the same. It
is created with the plain value `PhantomData`. The leading `_` in `_kind` is
the convention for a field that is never read. And now the mix-up is caught:

```text
error[E0308]: mismatched types
  |
7 | pub fn f() -> u64 { find_user(order_id()) }
  |                     --------- ^^^^^^^^^^ expected `Id<User>`, found `Id<Order>`
  |                     |
  |                     arguments to this function are incorrect
```

## Typestate: states as types

Many objects go through **states** with rules about what is allowed in
each: a connection must be opened before it is read; a request needs a URL
before it can be sent; a file must not be written after it is closed. The
usual way to enforce these is a field like `state: State` and a check at the
top of every method, which fails at run time, if it is remembered at all.

**Typestate** encodes each state as a separate **type**, and puts each
method only on the state where it makes sense:

```rust
pub struct Empty;
pub struct Ready;

pub struct Conn<S> {
    addr: String,
    _s: PhantomData<S>,
}

impl Conn<Empty> {
    pub fn new() -> Self { ... }
    pub fn connect(self, addr: &str) -> Conn<Ready> { ... }   // consumes the Empty one
}

impl Conn<Ready> {
    pub fn send(&self, msg: &str) { ... }                     // only exists when Ready
}
```

(A fragment.) `Empty` and `Ready` are empty structs, never created: they
exist only as names to put inside `Conn<...>`. The pieces fit together like
this:

- `impl Conn<Empty>` and `impl Conn<Ready>` are separate `impl` blocks, one
  per state (Beginner lesson 12 showed an `impl` for only some `T`). A
  `Conn<Empty>` has `new` and `connect`; a `Conn<Ready>` has `send`.
- A **transition** such as `connect` takes `self` **by value** and returns
  the struct in its new state. The old `Conn<Empty>` is moved into the
  method, so it cannot be used afterwards: you cannot keep a stale handle to
  an earlier state.
- The data (`addr`) is carried along from state to state.

```text
 Conn::new() ──> Conn<Empty> ──connect(addr)──> Conn<Ready> ──send(msg)
                     │                              │
                 has: connect                    has: send
```

Calling a method in the wrong state is now a compile error, and the
compiler's note even says where the method does exist:

```rust
Conn::new().send("hi")
```

```text
error[E0599]: no method named `send` found for struct `Conn<Empty>` in the current scope
  --> src/lib.rs:11:36
   |
 4 | pub struct Conn<S> { addr: String, _s: PhantomData<S> }
   | ------------------ method `send` not found for this struct
...
11 | pub fn f() -> String { Conn::new().send("hi") }
   |                                    ^^^^ method not found in `Conn<Empty>`
   |
   = note: the method was found for `Conn<Ready>`
```

Since `PhantomData` is zero-sized, all of this costs nothing at run time: a
`Conn<Ready>` is only a `String`. The checks happened entirely while
compiling. A typestate builder is used as a chain, each call returning the
next state: `Request::new().url("/x").header("A", "1").send()`.

## Run it

```rust
use std::marker::PhantomData;

trait Unit {
    const SYMBOL: &'static str;
    const PER_METER: f64;
}

struct Km;
impl Unit for Km {
    const SYMBOL: &'static str = "km";
    const PER_METER: f64 = 0.001;
}

struct Cm;
impl Unit for Cm {
    const SYMBOL: &'static str = "cm";
    const PER_METER: f64 = 100.0;
}

fn label<U: Unit>(meters: f64) -> String {
    format!("{} {}", meters * U::PER_METER, U::SYMBOL)
}

struct Empty;
struct Ready;

struct Conn<S> {
    addr: String,
    _s: PhantomData<S>,
}

impl Conn<Empty> {
    fn new() -> Self {
        Conn { addr: String::new(), _s: PhantomData }
    }
    fn connect(self, addr: &str) -> Conn<Ready> {
        Conn { addr: addr.to_string(), _s: PhantomData }
    }
}

impl Conn<Ready> {
    fn send(&self, msg: &str) -> String {
        format!("{} <- {msg}", self.addr)
    }
}

fn summarize<T, K, F>(items: &[T], key: F) -> Vec<K>
where
    F: Fn(&T) -> K,
    K: Ord + Clone,
{
    let mut keys: Vec<K> = items.iter().map(key).collect();
    keys.sort();
    keys.dedup();
    keys
}

fn main() {
    println!("{} | {}", label::<Km>(1500.0), label::<Cm>(1.5));
    println!("{}", Conn::new().connect("10.0.0.1:80").send("hi"));
    println!("{}", std::mem::size_of::<PhantomData<String>>());
    println!("{:?}", summarize(&["kiwi", "fig", "pear"], |w| w.len()));
}
```

```output
1.5 km | 150 cm
10.0.0.1:80 <- hi
0
[3, 4]
```

One generic `label` gave two units, with the constants chosen by the type
alone. `size_of::<PhantomData<String>>()` is 0: the marker takes no space.
`summarize` collected the key of each word (4, 3, 4), then sorted and
removed duplicates.

## Your turn

In `src/lib.rs`:

- trait `Shape` with an associated constant `const SIDES: u32` and an
  associated function `fn name() -> &'static str` (no `self`); implement it
  for `Triangle` (3, `"triangle"`) and `Square` (4, `"square"`)
- `total_sides::<A, B>()`: `A`'s sides plus `B`'s, with no arguments at
  all: `total_sides::<Triangle, Square>()` is 7
- `Meters<T>` (given) uses `PhantomData<T>` as a tag, so `Meters<Height>`
  and `Meters<Width>` are different types. Add `Meters::new(value)` (for any
  `T`), `value()`, and a free function
  `area(h: Meters<Height>, w: Meters<Width>) -> f64` that multiplies them.
  The tests check a `Meters` is no bigger than an `f64`.
- the typestate `Request` builder:
  - `Request::new()` (given) starts in state `Empty`
  - `.url(u)`, only on `Request<Empty>`, consumes it and returns a
    `Request<HasUrl>`
  - `.header(k, v)` and `.send()` exist **only** on `Request<HasUrl>`.
    `header` takes `self` and returns `Self`, so calls can be chained.
  - `send()` returns `"GET <url> [<k>: <v>, ...]"`, headers in the order they
    were added, separated by `", "`: `"GET https://example.com [Accept: json,
    X-Id: 7]"`, or `"GET /health []"` with no headers
  - the tests read your source, and fail if `fn send` or `fn header`
    appear inside the `impl Request<Empty>` block
- `largest_by(items, key)`, with the `where` clause given: the item whose
  key is largest, as `Some(&item)`; `None` for an empty slice.
  `largest_by(&["pear", "fig", "banana", "kiwi"], |w| w.len())` is
  `Some(&"banana")`. `K` is only `PartialOrd`, so compare keys with `>`
  rather than sorting.
