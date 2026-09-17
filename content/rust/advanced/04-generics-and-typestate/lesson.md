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

## where clauses

When bounds get long, move them after the signature:

```rust
fn summarize<T, K, F>(items: &[T], key: F) -> Vec<K>
where
    F: Fn(&T) -> K,
    K: Ord + Clone,
{ ... }
```

Same meaning as inline bounds, easier to read.

## Associated constants

Traits can require constants, available without any value:

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

The type parameter is chosen with the turbofish, `::<Km>`, since there is no argument to infer it from.

## PhantomData

A struct can be generic over a type it does not store. The compiler insists every
type parameter is used, so you mark it with a zero-sized `PhantomData`:

```rust
use std::marker::PhantomData;

struct Id<T> {
    value: u64,
    _kind: PhantomData<T>,
}

type UserId = Id<User>;
type OrderId = Id<Order>;      // cannot be passed where a UserId is expected
```

Zero runtime cost, and mixing up two kinds of id becomes a type error.

## Typestate: states as types

A builder or protocol has rules: "set the URL before sending", "open before
reading". Encode each state as a type, and give each state only the methods that
make sense there:

```rust
pub struct Empty;
pub struct Ready;

pub struct Conn<S> { addr: String, _s: PhantomData<S> }

impl Conn<Empty> {
    pub fn new() -> Self { ... }
    pub fn connect(self, addr: &str) -> Conn<Ready> { ... }   // consumes Empty
}

impl Conn<Ready> {
    pub fn send(&self, msg: &str) { ... }                        // only when Ready
}

Conn::new().send("hi");     // compile error: no method `send` on Conn<Empty>
```

Because transitions take `self` by value, the old state cannot be used after
the transition either. A whole class of runtime checks becomes a compile-time
guarantee.

## Your turn

In `src/lib.rs`:

- trait `Shape` with `const SIDES: u32` and `fn name() -> &'static str`,
  implemented for `Triangle` (3) and `Square` (4); `total_sides::<A, B>()`
- `Meters<T>` with a `PhantomData<T>` tag so `Meters<Height>` and
  `Meters<Width>` are different types; `Meters::new(value)`, `value()`, and
  `area(h: Meters<Height>, w: Meters<Width>) -> f64`
- a typestate `Request` builder: `Request::new()` (state `Empty`), `.url(u)`
  moves to `HasUrl`; only `HasUrl` offers `.header(k, v)` and `.send()`,
  which returns `"GET <url> [k: v, ...]"` (headers in insertion order)
- `largest_by(items, key)` using a `where` clause
