---
title: Patterns in depth
summary: Slice patterns, @ bindings, nested destructuring, match guards, let-else and matches!.
order: 6
files: [src/lib.rs]
run: cargo test
hints:
  - "`describe_slice`: `match items { [] => ..., [one] => ..., [first, .., last] => ... }`. A two-item slice also matches `[first, .., last]` with `..` empty."
  - "`classify_age`: `match age { 0 => \"newborn\", 1..=12 => \"child\", teen @ 13..=19 => ..., _ => \"adult\" }`, where the teen arm formats `teen`."
  - "`parse_kv`: `let Some((key, value)) = line.split_once('=') else { return None; };` then trim both and reject an empty key."
  - "`total_shipping`: iterate `for order in orders` and `match order { Order { items, destination: Destination::Domestic { express: true }, .. } => ..., ... }`."
---

`match` and `let` accept **patterns**, and patterns can take apart far more than
simple enums.

## Slice patterns

```rust
fn summary(xs: &[i32]) -> String {
    match xs {
        [] => "empty".into(),
        [x] => format!("just {x}"),
        [first, second] => format!("{first} and {second}"),
        [first, .., last] => format!("{first} ... {last}"),   // .. matches any number
    }
}
```

`[head, rest @ ..]` binds the remainder as a slice, which makes recursive
processing of slices natural.

## @ bindings

Test against a pattern **and** keep the value:

```rust
match port {
    p @ 1..=1023 => format!("privileged port {p}"),
    p @ 1024..=49151 => format!("registered port {p}"),
    p => format!("dynamic port {p}"),
}
```

## Nested destructuring

Patterns nest through structs, enums, tuples and references:

```rust
struct Point { x: i32, y: i32 }
enum Shape { Circle { center: Point, radius: u32 }, Line(Point, Point) }

match shape {
    Shape::Circle { center: Point { x: 0, y: 0 }, radius } => format!("centred, r={radius}"),
    Shape::Circle { radius, .. } => format!("r={radius}"),
    Shape::Line(Point { x: x1, .. }, Point { x: x2, .. }) if x1 == x2 => "vertical".into(),
    Shape::Line(..) => "line".into(),
}
```

`..` ignores the remaining fields. A **guard** (`if ...`) adds a condition the
pattern language cannot express.

## let-else

Destructure or bail out, without nesting the rest of the function:

```rust
fn port_of(addr: &str) -> Option<u16> {
    let Some((_, port)) = addr.rsplit_once(':') else {
        return None;
    };
    port.parse().ok()
}
```

The `else` block must diverge (`return`, `break`, `continue` or panic).

## matches! and if let chains

```rust
let is_vowel = matches!(c, 'a' | 'e' | 'i' | 'o' | 'u');

if let Some(user) = find(id)
    && user.active
{
    greet(user);
}
```

(`if let` chains with `&&` are stable in edition 2024.)

## Irrefutable patterns

`let (a, b) = pair;` and function parameters like `fn dist(&(x, y): &(f64, f64))`
use patterns too; they must always match.

## Your turn

In `src/lib.rs`:

- `describe_slice(items: &[&str])`: `"nothing"`, `"only a"`, or `"a to c (3 items)"`
- `classify_age(age: u32)`: `"newborn"` (0), `"child"` (1 to 12),
  `"teenager aged 15"` (13 to 19, with `@`), `"adult"`
- `parse_kv(line)`: `"key = value"` into `Some(("key", "value"))` trimmed, using
  `let-else`; `None` without `=` or with an empty key
- `sum_pairs(values: &[i32])`: add neighbours in pairs using `[a, b, rest @ ..]`
  recursion: `[1, 2, 3, 4, 5]` gives `[3, 7, 5]`
- `total_shipping(orders)`: per order, `Domestic { express: true }` costs 15,
  `Domestic` otherwise 5, `International { country }` costs 30 except `"SG"`
  which costs 20; orders with no items ship free
