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
