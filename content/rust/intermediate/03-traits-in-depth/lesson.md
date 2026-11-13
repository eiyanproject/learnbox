---
title: Traits in depth
summary: Associated types, operator overloading, generic traits with defaults, supertraits and blanket implementations.
order: 3
files: [src/lib.rs]
run: cargo test
hints:
  - "`impl Add for Money { type Output = Money; fn add(self, rhs: Money) -> Money { Money::new(self.cents + rhs.cents) } }`. `Mul<i64>` is `impl Mul<i64> for Money` with `rhs: i64`."
  - "`impl<T> Container for Stack<T> { type Item = T; fn get(&self, i: usize) -> Option<&T> { self.items.get(i) } fn len(&self) -> usize { self.items.len() } }`; `first` and `is_empty` are defaults in the trait, written with `get` and `len`."
  - "The supertrait: `pub trait Describe: fmt::Display { fn describe(&self) -> String { format!(\"<{}>\", self) } }`. The default body can use `Display` because every implementer must have it."
  - "The blanket impl: `impl<T: fmt::Display> Describe for T {}` gives every displayable type `describe()` for free. `Money` needs its own `Display` impl."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **associated type** | a type each implementation picks: `type Item = u32;` |
| **`Self::Item`** | the `Item` the implementing type chose |
| **one per type** | an associated type gives exactly one answer; a generic trait could have many |
| **generic parameter** (on a trait) | when one type can do the job for several others, like `Mul<f64>` |
| **default type parameter** | `trait Add<Rhs = Self>`: `Rhs` is `Self` unless you say otherwise |
| **operator overloading** | implementing `std::ops` traits so `+`, `-`, `*` work on your type |
| **right-hand side** (`Rhs`) | the type on the right of the operator |
| **`Output`** | the operator's result type |
| **supertrait** | `trait Shape: Debug`: every `Shape` must also be `Debug` |
| **blanket implementation** | `impl<T: Display> Shout for T`: for every type that meets the bound |
| **conflicting implementations** | two impls that could apply to one type; refused |
| **orphan rule** | the trait or the type must be defined in your crate |
| **newtype** | a one-field tuple struct wrapping an outside type, so you can implement traits for it |
| **static** vs **dynamic dispatch** | a copy per type, fast / one copy through a pointer, at run time |
| **`dyn Container<Item = u8>`** | a trait object must state its associated type |
| **absolute value** | the number without its sign: `cents.abs()` |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo test` | compiles and runs the tests |

### Rust names

| Name | What it does |
|---|---|
| `trait Container { type Item; fn get(&self, i: usize) -> Option<&Self::Item>; fn len(&self) -> usize; }` | a trait with an associated type |
| `fn first(&self) -> Option<&Self::Item> { self.get(0) }` | a default built on `get` |
| `impl<T> Container for Stack<T> { type Item = T; ... }` | an implementation for every `T` |
| `impl Add for Money { type Output = Money; fn add(self, o: Money) -> Money { ... } }` | `a + b` |
| `impl Sub`, `impl Mul<i64>`, `impl Neg`, `impl AddAssign` | `-`, `* 3`, unary `-`, `+=` |
| `use std::ops::{Add, Sub, Mul, Neg, AddAssign};` | brings the operator traits in |
| `trait Describe: Display { fn describe(&self) -> String { format!("<{self}>") } }` | a supertrait with a default |
| `impl<T: Display> Describe for T {}` | the blanket impl |
| `fn total_len<A: Container, B: Container>(a: &A, b: &B) -> usize` | two different container types |
| `write!(f, "{sign}{}.{:02}", c / 100, c % 100)` | units and two-digit cents |

### Errors

| Error | Means |
|---|---|
| `error[E0046]: not all trait items implemented, missing: Item` | the associated type was left out |
| `error[E0369]: cannot add Meters to Meters` | `+` without an `Add` impl |
| `error[E0119]: conflicting implementations of trait` | a specific impl overlapping a blanket one |
| `error[E0117]: only traits defined in the current crate can be implemented for types defined outside of the crate` | the orphan rule; use a newtype |

---

Beginner lesson 10 covered the core of traits: define one, implement it,
use it as a bound or as `dyn Trait`. This lesson covers the four features
that the standard library is built from, and that you will meet in every
real crate's documentation:

1. **associated types**: a type the implementer picks, like `Iterator::Item`;
2. **operator overloading**: `+`, `-`, `*` and friends are traits too;
3. **supertraits**: "to implement this trait, you must also implement that
   one";
4. **blanket implementations**: implementing a trait for *every* type that
   meets a bound, in one line.

## Associated types

A trait can declare a type, with `type Name;`, that each implementation
fills in. `Iterator` is the best-known example:

```rust
pub trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
}
```

(How the standard library declares it, shortened.) `Self::Item` means "the
`Item` type that the implementing type chose". An iterator over words sets
`type Item = &str;`, a counter sets `type Item = u32;`. Leave it out, and the
compiler asks for it:

```text
error[E0046]: not all trait items implemented, missing: `Item`
  |
2 | impl Iterator for Squares {
  | ^^^^^^^^^^^^^^^^^^^^^^^^^ missing `Item` in implementation
  |
  = help: implement the missing item: `type Item = /* Type */;`
```

Why not a generic trait, `trait Iterator<T>`? Because of what it would
allow. A type can implement a generic trait several times, once per `T`:
`Squares` could be both an `Iterator<u32>` and an `Iterator<String>`. Then
every `for x in squares` would have to say which one it meant, and the
compiler could not work out the type of `x` alone. An associated type means
"**exactly one** per implementing type": a `Squares` produces `u32`, full
stop.

The rule of thumb that follows:

- **associated type** when each type has one natural answer (what does this
  iterator produce?);
- **generic parameter** when one type can sensibly do the job for several
  others (you can add a `Meters` to a `Meters`, *and* multiply it by an
  `f64`, below).

## Operator overloading

Rust's operators are shorthand for trait methods in `std::ops`. `a + b`
calls `Add::add(a, b)`; `-a` calls `Neg::neg(a)`. Using `+` on your own type
without implementing the trait fails, and the error names the trait to
implement:

```text
error[E0369]: cannot add `Meters` to `Meters`
  |
3 | pub fn f() -> Meters { Meters(1.0) + Meters(2.0) }
  |                        ----------- ^ ----------- Meters
  |                        |
  |                        Meters
  |
note: an implementation of `Add` might be missing for `Meters`
```

Implementing it:

```rust
use std::ops::{Add, Mul};

#[derive(Debug, Clone, Copy, PartialEq)]
struct Meters(f64);

impl Add for Meters {
    type Output = Meters;
    fn add(self, rhs: Meters) -> Meters {
        Meters(self.0 + rhs.0)
    }
}

impl Mul<f64> for Meters {            // Meters * f64
    type Output = Meters;
    fn mul(self, k: f64) -> Meters {
        Meters(self.0 * k)
    }
}
```

The operator traits use both features from the section above:

- The **generic parameter** is the type on the right-hand side. `Add`
  declares it as `trait Add<Rhs = Self>`: a generic parameter *with a
  default*, so a plain `impl Add for Meters` means `Add<Meters>`, "a
  `Meters` plus a `Meters`". `impl Mul<f64> for Meters` is "a `Meters`
  times an `f64`". One type may implement `Mul` for several right-hand
  types.
- The **associated type** `Output` is the type of the result. For each pair
  of operand types there is exactly one result type.

The methods take `self` by value, so `a + b` moves `a` and `b`. For a small
`Copy` type like `Meters` that costs nothing and `a` stays usable; that is
why such types usually derive `Copy`.

Other operator traits work the same way:

| Trait | Operator | Method |
|---|---|---|
| `Add`, `Sub`, `Mul`, `Div`, `Rem` | `+ - * / %` | `fn add(self, rhs) -> Output` |
| `Neg` | `-x` (unary) | `fn neg(self) -> Output` |
| `AddAssign`, `SubAssign`, ... | `+=`, `-=`, ... | `fn add_assign(&mut self, rhs)`, changes in place, returns nothing |
| `Index`, `IndexMut` | `v[i]` | returns a reference to the item |

Comparison (`==`, `<`) is `PartialEq` and `PartialOrd`, from `std::cmp`, and
usually derived. Overload operators only where the meaning is obvious:
`money + money` is; `user + group` is not.

## Supertraits

A trait can require another trait from every implementer:

```rust
trait Shape: std::fmt::Debug {
    fn area(&self) -> f64;

    fn report(&self) -> String {
        format!("{self:?} has area {}", self.area())   // Debug is guaranteed
    }
}
```

`trait Shape: Debug` reads "a `Shape` is something that is also `Debug`";
`Debug` is the **supertrait**. It has two effects:

- Implementing `Shape` for a type that does not implement `Debug` is a
  compile error. The requirement is checked once, at the `impl`.
- In return, code inside the trait, and any code holding a `T: Shape`, may
  use `Debug` without asking for it separately. That is what lets the
  default `report` method write `{self:?}`.

A supertrait is not inheritance: `Shape` does not get `Debug`'s methods
copied into it, and the `Debug` implementation is written separately (here,
derived).

## Blanket implementations

So far each `impl` was for one named type. A **blanket implementation** is
for every type that satisfies a bound:

```rust
trait Shout {
    fn shout(&self) -> String;
}

impl<T: std::fmt::Display> Shout for T {
    fn shout(&self) -> String {
        self.to_string().to_uppercase()
    }
}

42.shout();       // "42"
"hi".shout();     // "HI"
```

`impl<T: Display> Shout for T` reads: "for any type `T` that implements
`Display`, here is its `Shout`". Integers, strings, and any of your own types
that implement `Display`, now or in the future, all get `.shout()` at once.
The standard library does this constantly: the `to_string()` you have been
calling is from `impl<T: Display> ToString for T`, which is why implementing
`Display` gave you `to_string` for free in Beginner lesson 10.

A blanket impl covers its types completely: you cannot also write a
specific `impl Shout for MyType` for a type that is `Display`. The compiler
cannot pick between two implementations, so it refuses both:

```text
error[E0119]: conflicting implementations of trait `Shout` for type `M`
  |
3 | impl<T: fmt::Display> Shout for T {
  | --------------------------------- first implementation here
...
6 | impl Shout for M {
  | ^^^^^^^^^^^^^^^^ conflicting implementation for `M`
```

### The orphan rule

There is one restriction on which impls you may write at all, the **orphan
rule**: at least one of the trait or the type must be defined in your own
crate. You may implement your trait for `i32`, or `Display` for your type,
but not `Display` for `Vec<i32>`:

```text
error[E0117]: only traits defined in the current crate can be implemented for types defined outside of the crate
  |
2 | impl fmt::Display for Vec<i32> {
  | ^^^^^^^^^^^^^^^^^^^^^^--------
  |                       |
  |                       `Vec` is not defined in the current crate
  |
  = note: define and implement a trait or new type instead
```

The reason: if two crates could both implement `Display` for `Vec<i32>`, a
program using both would have two conflicting implementations, and neither
crate's author could have prevented it. The `note:` gives the standard
workaround, a **newtype**: a one-field tuple struct such as
`struct Numbers(Vec<i32>);`, which is your type, so you can implement
anything for it.

## Generic functions vs trait objects, again

`fn total<T: Container>(c: &T)` is compiled once per type it is used with
(static dispatch: fast, but more machine code). `fn total(c: &dyn Container)`
is compiled once and works through a pointer at run time (dynamic dispatch).
With associated types there is a catch: a `dyn Container` must say its item
type, as in `&dyn Container<Item = u8>`, because code using it has to know
what `get` returns. Generic methods (a method with its own `<T>`) make a
trait unusable as `dyn` at all. Both are reasons generics are the default in
Rust and trait objects the exception.

## Run it

```rust
use std::fmt::{Debug, Display};
use std::ops::{Add, Mul};

#[derive(Debug, Clone, Copy, PartialEq)]
struct Meters(f64);

impl Add for Meters {
    type Output = Meters;
    fn add(self, rhs: Meters) -> Meters {
        Meters(self.0 + rhs.0)
    }
}

impl Mul<f64> for Meters {
    type Output = Meters;
    fn mul(self, k: f64) -> Meters {
        Meters(self.0 * k)
    }
}

trait Shape: Debug {
    fn area(&self) -> f64;
    fn report(&self) -> String {
        format!("{self:?} has area {}", self.area())
    }
}

#[derive(Debug)]
struct Square(f64);

impl Shape for Square {
    fn area(&self) -> f64 {
        self.0 * self.0
    }
}

trait Shout {
    fn shout(&self) -> String;
}

impl<T: Display> Shout for T {
    fn shout(&self) -> String {
        self.to_string().to_uppercase()
    }
}

fn main() {
    let a = Meters(1.5);
    println!("{:?} {:?}", a + Meters(2.0) * 2.0, a);
    println!("{}", Square(3.0).report());
    println!("{} {}", 42.shout(), "hi".shout());
}
```

```output
Meters(5.5) Meters(1.5)
Square(3.0) has area 9
42 HI
```

`*` binds tighter than `+`, exactly as with numbers, so the first line is
1.5 + (2.0 × 2.0). `a` was moved into `+`, but it is `Copy`, so it is still
printable afterwards. `report` came from the trait's default and used
`Debug` through the supertrait.

## Your turn

In `src/lib.rs`:

- `Money { cents: i64 }` (already defined, and `Copy`) supports:
  - `a + b` and `a - b` between two `Money` values
  - `money * 3`, a `Money` times an `i64`
  - `-money` (`Neg`)
  - `a += b` (`AddAssign`)
- `Display` for `Money`, as units and two-digit cents: `1234` cents is
  `12.34`, `5` is `0.05`, `100000` is `1000.00`. Negative amounts put the
  sign in front: `-50` is `-0.50`. Careful: `-50 / 100` is `0`, which has
  no sign, so print the sign yourself and then format the **absolute** value
  (`cents.abs()`).
- trait `Container` with:
  - an associated type `Item`
  - required methods `get(&self, i: usize) -> Option<&Self::Item>` and
    `len(&self) -> usize`
  - **default** methods `first()` (the item at 0, as `Option<&Self::Item>`)
    and `is_empty()`, written using `get` and `len`. The tests implement
    `Container` for a type of their own with only `get` and `len`, and call
    `first` on it, so these really must be defaults.
- implement `Container` for `Stack<T>`, for every `T`
- `total_len(a, b)`: the sum of the lengths of two containers, which may be
  of **different** types (the signature already has two parameters, `A` and
  `B`, for that)
- trait `Describe` with supertrait `Display` and a default `describe()`
  returning `<`, the display text, and `>`: `42.describe()` is `"<42>"`.
  Implement it for every `Display` type with a single blanket impl; `Money`
  then gets it through its `Display`.
