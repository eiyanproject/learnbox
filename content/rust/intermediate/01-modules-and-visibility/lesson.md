---
title: Modules and visibility
summary: Split a crate across files, control what is public with pub and pub(crate), and shape the API with use and re-exports.
order: 1
files: [src/lib.rs, src/shapes.rs, src/shapes/circle.rs, src/units.rs]
run: cargo test
hints:
  - "`src/lib.rs` declares the modules with `pub mod shapes;` and `mod units;` (private), and re-exports with `pub use shapes::circle::Circle;`."
  - "`src/shapes.rs` is the `shapes` module; it declares its child with `pub mod circle;`, which lives in `src/shapes/circle.rs`."
  - "Inside `circle.rs`, reach the private `units` module through the crate root: `use crate::units::round2;`. `pub(crate)` makes `round2` visible anywhere in the crate but not to users."
  - "`Circle` needs `pub` on the struct, on `new`, and on each method the tests call. Keep the `radius` field private and expose `radius()`."
---

Everything so far lived in one `lib.rs`. Real crates split code into
**modules**, and Rust makes you say exactly what each module exposes.

## Declaring modules

A module is declared with `mod` in its parent. The body can be inline:

```rust
mod network {
    pub fn connect() {}
}
```

or in a file. `mod shapes;` in `src/lib.rs` tells the compiler to load
`src/shapes.rs` (or `src/shapes/mod.rs`, the older layout). A child of `shapes`
declared inside `shapes.rs` with `pub mod circle;` lives in `src/shapes/circle.rs`:

```text
src/
├── lib.rs            crate root:        mod shapes; mod units;
├── shapes.rs         module shapes:     pub mod circle;
├── shapes/
│   └── circle.rs     module shapes::circle
└── units.rs          module units
```

Files are not modules by themselves. A file nobody declares with `mod` is not compiled at all.

## Privacy

**Everything is private by default**: visible in its own module and that
module's children, and nowhere else.

| Keyword | Visible to |
|---|---|
| (none) | this module and its children |
| `pub(super)` | the parent module |
| `pub(crate)` | the whole crate, but not its users |
| `pub` | everyone, if every enclosing module is reachable too |

Struct **fields** have their own visibility. A `pub struct` with private fields
can only be built through its own functions, which is how you keep invariants:

```rust
pub struct Percent {
    value: u8,          // private: nobody can make Percent { value: 250 }
}

impl Percent {
    pub fn new(value: u8) -> Option<Self> {
        (value <= 100).then_some(Self { value })
    }
    pub fn value(&self) -> u8 { self.value }
}
```

## Paths and use

```rust
crate::units::round2(x)       // absolute, from the crate root
super::helper()               // the parent module
self::inner::thing()          // this module

use crate::units::round2;     // bring a name into scope
use std::collections::{HashMap, HashSet};
use std::fmt::{self, Display};
```

## Re-exports: design the public API

Your file layout is an implementation detail. `pub use` lets users write
`my_crate::Circle` instead of `my_crate::shapes::circle::Circle`, and lets you
reorganise files later without breaking them:

```rust
// src/lib.rs
pub mod shapes;
pub use shapes::circle::Circle;
```

## Your turn

The files exist but the module tree is not wired up. Make these work from the
tests (an outside user of the crate):

- `modules_lesson::Circle` (re-exported) and `modules_lesson::shapes::circle::Circle` are the same type
- `Circle::new(radius)` with a **private** `radius` field and a `radius()` getter
- `area()` and `circumference()`, both rounded to 2 decimal places by
  `units::round2`
- `units` stays private to the crate: `round2` is `pub(crate)`
- `shapes::describe(&Circle)` returns `"circle r=1.5 area=7.07"`
