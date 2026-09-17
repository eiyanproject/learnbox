---
title: Traits in depth
summary: Associated types, operator overloading, generic traits with defaults, supertraits and blanket implementations.
order: 3
files: [src/lib.rs]
run: cargo test
hints:
  - "`impl Add for Money { type Output = Money; fn add(self, rhs: Money) -> Money { Money::new(self.cents + rhs.cents) } }`. `Mul<i64>` is `impl Mul<i64> for Money` with `rhs: i64`."
  - "`impl Container for Stack<T> { type Item = T; fn get(&self, i: usize) -> Option<&T> { self.items.get(i) } fn first(&self) -> Option<&T> { self.items.first() } }`, and the `len` part the trait needs."
  - "The supertrait: `pub trait Describe: fmt::Display { fn describe(&self) -> String { format!(\"<{}>\", self) } }`. The default body can use `Display` because every implementer must have it."
  - "The blanket impl: `impl<T: fmt::Display> Describe for T {}` gives every displayable type `describe()` for free. `Money` needs its own `Display` impl."
---

## Associated types

A trait can name a type that each implementation chooses. `Iterator` is the
famous example:

```rust
pub trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
}
```

Why not `trait Iterator<T>`? A generic trait could be implemented many times
for one type (an iterator of `i32` **and** of `String`), and every use would
need to say which. An associated type means "exactly one per implementor", so
`for x in things` knows what `x` is.

## Operator overloading

Operators are traits in `std::ops`:

```rust
use std::ops::{Add, Mul, Neg, Index};

#[derive(Debug, Clone, Copy, PartialEq)]
struct Meters(f64);

impl Add for Meters {
    type Output = Meters;
    fn add(self, rhs: Meters) -> Meters { Meters(self.0 + rhs.0) }
}

impl Mul<f64> for Meters {            // Meters * f64
    type Output = Meters;
    fn mul(self, k: f64) -> Meters { Meters(self.0 * k) }
}
```

The generic parameter is the right-hand side type (`Add<Rhs = Self>` defaults
to the same type). `AddAssign` gives `+=`, `Index` gives `v[i]`, `Neg` gives `-x`.
Comparison is `PartialEq`/`PartialOrd`, usually derived.

## Supertraits

A trait can require another:

```rust
trait Shape: std::fmt::Debug {
    fn area(&self) -> f64;
    fn report(&self) -> String {
        format!("{self:?} has area {}", self.area())   // Debug is guaranteed
    }
}
```

## Blanket implementations

Implement a trait for **every** type that meets a bound:

```rust
trait Shout {
    fn shout(&self) -> String;
}

impl<T: std::fmt::Display> Shout for T {
    fn shout(&self) -> String { self.to_string().to_uppercase() }
}

42.shout();       // "42"
"hi".shout();     // "HI"
```

The standard library does this constantly: every `T: Display` gets `ToString`
this way. (The orphan rule stops you implementing foreign traits for foreign
types; at least one of them must be defined in your crate.)

## Generic functions vs trait objects

`fn total<T: Container>(c: &T)` is compiled separately for each `T` (static
dispatch, no runtime cost). `&dyn Container` works with any implementor at
runtime (dynamic dispatch, one function). Traits with associated types or
generic methods have restrictions as trait objects, which is one reason both
styles exist.

## Your turn

In `src/lib.rs`:

- `Money { cents: i64 }` supports `a + b`, `a - b`, `money * 3` (an `i64`),
  `-money`, and `+=`; `Display` shows `12.34` style (negative: `-0.50`)
- trait `Container` with associated type `Item`, required methods
  `get(&self, i) -> Option<&Self::Item>` and `len(&self) -> usize`, and default
  methods `first()` and `is_empty()`; implement it for `Stack<T>`
- `total_len(a, b)`: sum of lengths of any two containers, generic over both
- trait `Describe: Display` with a default `describe()` returning `<` + the
  display text + `>`, implemented for every `Display` type with one blanket impl
