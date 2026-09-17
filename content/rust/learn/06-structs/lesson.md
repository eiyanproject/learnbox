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
how the method uses the value: `&self` to read, `&mut self` to change, `self`
to take ownership.

## derive

Structs get almost no behaviour for free. `#[derive]` generates common
trait implementations:

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

## Your turn

In `src/lib.rs`, implement the `Rectangle` methods:

- `Rectangle::new(width, height)`
- `Rectangle::square(size)`
- `area()` and `perimeter()`
- `can_hold(other)`: `true` if `other` fits strictly inside, both width and
  height smaller. No rotating.
- `scale(factor)`: multiply both sides, changing the rectangle
