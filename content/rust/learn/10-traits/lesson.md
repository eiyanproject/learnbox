---
title: Traits
summary: Shared behaviour across types, default methods, trait bounds, and dyn for mixed collections.
order: 10
files: [src/lib.rs]
run: cargo test
hints:
  - "Implement the trait per type: `impl Shape for Circle { fn area(&self) -> f64 { PI * self.radius * self.radius } fn name(&self) -> String { \"circle\".to_string() } }`."
  - "The default `describe` is written once in the trait body and can call `self.name()` and `self.area()`: `format!(\"{} with area {:.2}\", self.name(), self.area())`."
  - "`impl fmt::Display for Square { fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result { write!(f, \"Square({})\", self.side) } }`."
  - "`total_area(shapes: &[Box<dyn Shape>])`: loop and add `shape.area()`. `largest<T: PartialOrd + Copy>`: keep the biggest seen so far, starting from `items[0]`."
---

A **trait** describes behaviour that several types can share, like an
interface in other languages.

```rust
trait Speak {
    fn speak(&self) -> String;
}

struct Dog;
struct Robot { id: u32 }

impl Speak for Dog {
    fn speak(&self) -> String {
        "woof".to_string()
    }
}

impl Speak for Robot {
    fn speak(&self) -> String {
        format!("unit {} online", self.id)
    }
}
```

## Default methods

A trait can provide a method body that implementers get for free, and may
override:

```rust
trait Speak {
    fn speak(&self) -> String;

    fn shout(&self) -> String {
        self.speak().to_uppercase() + "!"
    }
}
```

`Dog.shout()` now works without `Dog` writing anything more.

## Traits as bounds: static dispatch

A generic function can accept any type that implements a trait:

```rust
fn announce<T: Speak>(thing: &T) -> String {
    format!("It says: {}", thing.speak())
}

// shorter form of the same thing
fn announce(thing: &impl Speak) -> String { ... }
```

The compiler generates a copy of `announce` for each type it is used with,
so there is no runtime cost.

Bounds can combine traits: `T: PartialOrd + Copy` means "comparable, and
cheap to copy", exactly what finding a maximum needs.

## dyn: mixing types in one collection

A `Vec<T>` holds one type. To hold a `Dog` and a `Robot` together, store
**trait objects**:

```rust
let things: Vec<Box<dyn Speak>> = vec![Box::new(Dog), Box::new(Robot { id: 7 })];
for t in &things {
    println!("{}", t.speak());
}
```

`Box` puts each value on the heap so they can have different sizes;
`dyn Speak` means "some type that implements Speak, decided at runtime".

## Standard traits you implement often

| Trait | Gives you |
|---|---|
| `Debug` | `{:?}` formatting (usually derived) |
| `Display` | `{}` formatting and `.to_string()` (written by hand) |
| `Clone`, `Copy` | `.clone()`, implicit copies |
| `PartialEq`, `Eq` | `==` |
| `PartialOrd`, `Ord` | `<`, `>`, sorting |
| `Default` | `T::default()` |

Display looks like this:

```rust
use std::fmt;

impl fmt::Display for Robot {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "Robot #{}", self.id)
    }
}
```

## Your turn

In `src/lib.rs`:

- Implement `Shape` for `Circle` (name `"circle"`) and `Square` (name `"square"`)
- Give `Shape` a **default** `describe()` returning `"<name> with area <area>"`,
  area with 2 decimals: `"square with area 4.00"`
- Implement `Display` for `Square`: `Square(2)` for a side of `2.0`
- `total_area(shapes)`: the sum of all areas in a mixed list
- `largest(items)`: the largest item of a non-empty slice, for any type that
  is `PartialOrd + Copy`
