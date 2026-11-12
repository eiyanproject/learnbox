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

Every Beginner lesson kept all its code in one `src/lib.rs`. That stops
working at a few hundred lines: related code is hard to find, names collide,
and every function can reach into every struct. Rust's answer is the
**module**: a named container for functions, types and other modules, which
decides for each item whether code outside may use it.

Modules do two jobs:

- **Organisation**: group related code and give it a path, the way folders
  group files (`shapes::circle::Circle`).
- **Privacy**: hide the details, so the rest of the program can only use what
  a module deliberately offers. Hidden code can then be changed freely,
  because nothing outside depends on it.

A few words used below. A **crate** is one compiled unit, a library or a
program; this lesson's crate is the library `modules_lesson`. Its **crate
root** is the file the compiler starts from, `src/lib.rs` for a library. An
**item** is anything you can name in a module: a function, struct, enum,
trait, constant, or another module.

## Declaring modules

A module is declared with `mod` in its **parent** module. Its body can be
written inline, in braces:

```rust
mod network {
    pub fn connect() {}
}
```

(A fragment.) Or it can live in its own file: `mod shapes;`, ending in a
semicolon, tells the compiler "the body of module `shapes` is in a file".
Where the compiler looks depends on where the `mod` line is:

```text
src/
├── lib.rs            crate root, contains:   pub mod shapes;  mod units;
├── shapes.rs         module shapes, contains: pub mod circle;
├── shapes/
│   └── circle.rs     module shapes::circle
└── units.rs          module units
```

- `mod shapes;` in `src/lib.rs` loads `src/shapes.rs`.
- `mod circle;` in `src/shapes.rs` loads `src/shapes/circle.rs`: a child's
  file goes in a folder named after its parent.
- An older layout, `src/shapes/mod.rs` instead of `src/shapes.rs`, also
  works. You will see it in older code; this course uses the newer one.

The direction is important, and differs from Python or JavaScript: **a file
is not a module by itself**. It becomes one only when its parent declares it
with `mod`. A file that nobody declares is not compiled at all, so errors in
it go unreported and its functions do not exist. The other way round, a
`mod` line without its file is an error that tells you where to put it:

```text
error[E0583]: file not found for module `shapes`
 --> src/lib.rs:1:1
  |
1 | mod shapes;
  | ^^^^^^^^^^^
  |
  = help: to create the module `shapes`, create file "src/shapes.rs" or "src/shapes/mod.rs"
```

## Privacy

**Everything is private by default**: an item can be used by code in its own
module and that module's children (modules declared inside it), and nowhere
else. Calling a private function from outside:

```rust
mod units {
    fn round2(x: f64) -> f64 {
        (x * 100.0).round() / 100.0
    }
}

pub fn f() -> f64 {
    units::round2(1.0)
}
```

```text
error[E0603]: function `round2` is private
 --> src/lib.rs:7:12
  |
7 |     units::round2(1.0)
  |            ^^^^^^ private function
  |
note: the function `round2` is defined here
 --> src/lib.rs:2:5
  |
2 |     fn round2(x: f64) -> f64 {
  |     ^^^^^^^^^^^^^^^^^^^^^^^^
```

A visibility keyword in front of an item opens it up:

| Written | Usable from |
|---|---|
| (nothing) | this module and its children |
| `pub(super)` | also the parent module |
| `pub(crate)` | anywhere in this crate, but not by users of the crate |
| `pub` | anywhere, including other crates |

`pub` alone is not quite enough to reach an item from outside: every module
on the path to it must be reachable too. A `pub fn` inside a private `mod
units` is still invisible to users of the crate, because they cannot get
into `units`. That is how this lesson's exercise keeps `units` hidden while
`round2` is used throughout the crate: the module is private, and `round2`
is `pub(crate)`.

`pub(crate)` is the usual choice for helpers: shared inside the crate, not
promised to anyone outside. Everything marked `pub` and reachable is your
crate's **public API**, which users may come to depend on, so it should be a
deliberate list.

### Fields are private too

A struct's fields have their own visibility, separate from the struct's. A
`pub struct` with private fields can be *named* outside its module, but not
*built* or taken apart there:

```rust
mod units {
    pub struct Percent {
        value: u8,          // private: only code in units can touch it
    }

    impl Percent {
        pub fn new(value: u8) -> Option<Self> {
            (value <= 100).then_some(Self { value })
        }
        pub fn value(&self) -> u8 {
            self.value
        }
    }
}
```

(A fragment.) Outside `units`, `units::Percent { value: 250 }` fails with
``error[E0451]: field `value` of struct `Percent` is private``. The only way
to make a `Percent` is `Percent::new`, which refuses anything above 100, so
**every** `Percent` that exists anywhere in the program holds 0 to 100. A
rule that always holds like that is called an **invariant**, and private
fields are how Rust code protects one: there is no way around the check.
`bool::then_some(v)` gives `Some(v)` when the `bool` is `true`, `None`
otherwise. `value()` is a **getter**: a method that lets others read a
private field without being able to change it.

(Enum variants and their fields are the exception: in a `pub enum`,
everything is public, because an enum you cannot match on would be useless.)

## Paths and use

Items are reached by **paths**, with `::` between the parts, like folders in
a file path:

```rust
crate::units::round2(x)       // absolute: from the crate root
super::helper()               // relative: from the parent module
self::inner::thing()          // relative: from this module
```

(Path expressions.) `crate` always means "the root of this crate", wherever
you write it; `super` is ".." in a file path.

Writing `crate::units::round2` every time is long, so `use` creates a
shortcut: after it, the last part of the path can be used alone in that
module:

```rust
use crate::units::round2;             // now round2(x) works here
use std::collections::{HashMap, HashSet};   // several items from one path
use std::fmt::{self, Display};        // `fmt` itself, and fmt::Display
```

(Inside braces, `self` means the module named before them, so the last line
brings in both `fmt` and `Display`.)

`use` only creates a name; it does not grant access. `use crate::units::round2;`
fails with E0603 if `round2` is private. And a `use` applies only in the
module where it is written: `circle.rs` needs its own `use` lines, even if
`lib.rs` has the same ones.

## Re-exports: design the public API

Your file layout is an implementation detail, but the paths users write
follow it: `modules_lesson::shapes::circle::Circle` is long and exposes how
you happened to arrange files. `pub use` both brings a name into scope **and**
makes it public at the new place, which is called a **re-export**:

```rust
// src/lib.rs
pub mod shapes;
pub use shapes::circle::Circle;
```

Now users can write `modules_lesson::Circle`. It is not a copy or a new type:
both paths name the very same `Circle`. The benefit comes later: you can move
`Circle` to another file, update the `pub use` line, and no user's code
breaks. The standard library does this everywhere; `std::collections::HashMap`
is really defined in a deeper, private module.

## Run it

```rust
mod units {
    pub struct Percent {
        value: u8,
    }

    impl Percent {
        pub fn new(value: u8) -> Option<Self> {
            (value <= 100).then_some(Self { value })
        }
        pub fn value(&self) -> u8 {
            self.value
        }
    }

    pub(crate) fn round2(x: f64) -> f64 {
        (x * 100.0).round() / 100.0
    }

    pub mod inner {
        pub fn helper() -> f64 {
            super::round2(2.0 / 3.0)       // the parent module's function
        }
    }
}

use units::Percent;

fn main() {
    println!("{:?}", Percent::new(42).map(|p| p.value()));
    println!("{}", Percent::new(250).is_none());
    println!("{} {}", crate::units::round2(3.14159), units::inner::helper());
}
```

```output
Some(42)
true
3.14 0.67
```

This program is a single file, so its modules are inline, but the rules are
the same as with files. `main` is in the crate root, the parent of `units`,
and can use `round2` because it is `pub(crate)`. `inner` reaches `round2`
with `super::`, its parent. `Percent { value: 250 }` written in `main` would
not compile: the field is private to `units`, and `new` refused 250 with
`None`.

## Your turn

The four files exist, but nothing declares them, so the crate is one empty
`lib.rs`. Wire up the module tree so that the tests, which use the crate from
outside like any user would, can reach:

- `modules_lesson::Circle` (a re-export) and
  `modules_lesson::shapes::circle::Circle`, the same type
- `Circle::new(radius)`, with the `radius` field kept **private** (no
  `pub radius`) and a public `radius()` getter
- `area()` and `circumference()`, both rounded to 2 decimal places with
  `units::round2`: radius 1.0 gives 3.14 and 6.28
- `shapes::describe(&circle)`, a function in `src/shapes.rs`, returning
  `"circle r=1.5 area=7.07"` for radius 1.5

Three things are checked by reading your source, because privacy is hard to
test from outside:

- `src/lib.rs` has a line that is exactly `mod units;`, with no `pub`
- `src/units.rs` declares `pub(crate) fn round2`
- `src/shapes/circle.rs` contains `pub struct Circle` and no `pub radius`

Everything the tests call needs `pub`: the struct, `new`, and each method.
Expect a few E0603 errors along the way; each one names the item that needs
it.
