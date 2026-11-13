---
title: Structs and methods
summary: Define your own types, attach methods with impl, and derive common behaviour.
order: 6
files: [src/lib.rs]
run: cargo test
hints:
  - "`new` is an associated function: `pub fn new(width: u32, height: u32) -> Self { Self { width, height } }`."
  - "Reading methods take `&self`: `pub fn area(&self) -> u32 { self.width * self.height }`."
  - "`can_hold(&self, other: &Rectangle) -> bool`: both of this rectangle's sides must be strictly larger than the other's."
  - "`scale` changes the rectangle, so it takes `&mut self`. `square(size)` has no `self` at all: `Self::new(size, size)`."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **struct** | a type that groups related values under one name |
| **field** | one named part of a struct, with its type |
| **instance** | one value of a struct type |
| **field init shorthand** | writing `name` once when a variable and a field share the name |
| **tuple struct** | a struct with unnamed fields, such as `struct Meters(f64);` |
| **`impl` block** | where a type's methods and associated functions are written |
| **method** | a function whose first parameter is `self`, called with a dot |
| **`&self`** / **`&mut self`** / **`self`** | borrow to read / borrow to change / take ownership |
| **associated function** | a function in an `impl` with no `self`, called with `::`: `User::new` |
| **`Self`** | the type the `impl` is for |
| **constructor** (`new`) | the usual name for an associated function that builds a value |
| **attribute** | an annotation above an item, such as `#[derive(...)]` |
| **derive** | ask the compiler to generate common trait implementations |
| **`Debug`** | allows `{:?}` printing |
| **`Clone`** | adds `.clone()` |
| **`PartialEq`** | allows `==` and `!=`, field by field |
| **strictly inside** | smaller on both sides; equal does not count |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo test` | compiles and runs the tests |

### Rust names

| Name | What it does |
|---|---|
| `struct User { name: String, age: u32, active: bool }` | a struct |
| `User { name, age: 30, active: true }` | creates one, with field init shorthand for `name` |
| `ana.age += 1` | changes a field; the binding must be `mut` |
| `impl Rectangle { pub fn area(&self) -> u32 { ... } }` | a method |
| `Rectangle::new(3, 4)`, `Rectangle::square(5)` | associated functions |
| `r.scale(2)` | a `&mut self` method; Rust borrows `r` for you |
| `u.into_name()` | a `self` method: `u` is moved and cannot be used again |
| `#[derive(Debug, Clone, PartialEq)]` | generates those traits |
| `println!("{p:?}")` | debug printing |
| `assert_eq!(a, b)` | a test check; needs `PartialEq` and `Debug` |

### Errors

| Error | Means |
|---|---|
| `error[E0277]: Point doesn't implement Debug` | `{:?}` on a struct without `#[derive(Debug)]` |
| `value used after move` | the value was taken by a `self` method |
| `binary operation == cannot be applied to type` | comparing a struct without `PartialEq` |

---

A user has a name, an age and an active flag. Passing those around as three
separate variables, or as a tuple `(String, u32, bool)` where position 1
means age, gets confusing fast. A **struct** groups related values under one
name, with a name for each part, its **fields**. It is Rust's equivalent of a
class's data; the behaviour comes in `impl` blocks, below.

## Defining a struct

```rust
struct User {
    name: String,
    age: u32,
    active: bool,
}

let ana = User {
    name: String::from("Ana"),
    age: 31,
    active: true,
};
println!("{}", ana.name);
```

To change a field, the whole binding must be `mut`: `let mut ana = ...;
ana.age += 1;`.

Field init shorthand: when a variable has the same name as the field, write
it once.

```rust
fn make_user(name: String, age: u32) -> User {
    User { name, age, active: true }
}
```

## Tuple structs

Structs with unnamed fields are handy for giving a distinct type to a simple value:

```rust
struct Meters(f64);
let d = Meters(3.5);
d.0    // 3.5
```

## Methods with impl

```rust
impl User {
    // associated function: no self, called as User::new(...)
    fn new(name: &str, age: u32) -> Self {
        Self { name: name.to_string(), age, active: true }
    }

    // reads the struct
    fn is_adult(&self) -> bool {
        self.age >= 18
    }

    // changes the struct
    fn birthday(&mut self) {
        self.age += 1;
    }

    // consumes the struct
    fn into_name(self) -> String {
        self.name
    }
}

let mut u = User::new("Ana", 17);
u.birthday();
u.is_adult();    // true
```

`Self` is shorthand for the type the `impl` is for. The first parameter says
how the method uses the value, and it uses exactly the ownership rules of
the last two lessons:

| First parameter | Means | The caller keeps the value? |
|---|---|---|
| `&self` | borrow it to read | yes |
| `&mut self` | borrow it to change | yes, changed |
| `self` | take ownership | no: it is moved into the method |
| *(none)* | an **associated function**, not a method | (no value involved) |

So after `u.into_name()`, `u` has been moved and cannot be used again; the
compiler would say `value used after move`. Methods are called with a dot,
`u.birthday()`, and Rust borrows `u` automatically to match the first
parameter; you do not write `(&mut u).birthday()`. Associated functions are
called on the type with `::`, as `User::new(...)`, and `new` is the usual
name for the one that builds a value.

## derive

Structs get almost no behaviour for free: a new struct cannot be printed,
copied or compared with `==` until you say so. Try `println!("{p:?}")` on a
struct without `Debug` and the compiler says
``error[E0277]: `Point` doesn't implement `Debug` ``, with a `help:` suggesting
`#[derive(Debug)]`. The `#[derive]` attribute, written just above the struct,
generates common **trait** implementations (traits are lesson 10) for you:

- `Debug` allows `{:?}` printing, for developers and test messages;
- `Clone` adds `.clone()`, a deep copy;
- `PartialEq` allows `==` and `!=`, comparing field by field.

```rust
#[derive(Debug, Clone, PartialEq)]
struct Point {
    x: i32,
    y: i32,
}

let p = Point { x: 1, y: 2 };
println!("{p:?}");          // Debug: Point { x: 1, y: 2 }
let q = p.clone();          // Clone
assert_eq!(p, q);           // PartialEq, and Debug to print on failure
```

`assert_eq!` needs both `PartialEq` and `Debug`, which is why the starter
derives them.

## Run it

```rust
#[derive(Debug, Clone, PartialEq)]
struct Point {
    x: i32,
    y: i32,
}

struct Meters(f64);

struct User {
    name: String,
    age: u32,
    active: bool,
}

impl User {
    fn new(name: &str, age: u32) -> Self {
        Self { name: name.to_string(), age, active: true }
    }
    fn is_adult(&self) -> bool {
        self.age >= 18
    }
    fn birthday(&mut self) {
        self.age += 1;
    }
    fn into_name(self) -> String {
        self.name
    }
}

fn main() {
    let mut u = User::new("Ana", 17);
    println!("{} {}", u.is_adult(), u.active);
    u.birthday();
    println!("{} {}", u.age, u.is_adult());
    println!("{}", u.into_name());     // u is used up after this

    let d = Meters(3.5);
    println!("{}", d.0);

    let p = Point { x: 1, y: 2 };
    let q = p.clone();
    println!("{p:?} {}", p == q);
}
```

```output
false true
18 true
Ana
3.5
Point { x: 1, y: 2 } true
```

## Your turn

In `src/lib.rs`, implement the `Rectangle` methods:

- `Rectangle::new(width, height)`, an associated function
- `Rectangle::square(size)`, a rectangle with both sides `size`
- `area()` and `perimeter()`, which only read the rectangle (`&self`)
- `can_hold(other)`: `true` if `other` fits strictly inside: both its width
  and its height smaller than this rectangle's. Equal sides do not fit, and
  there is no rotating.
- `scale(factor)`: multiply both sides, changing this rectangle (`&mut self`)
