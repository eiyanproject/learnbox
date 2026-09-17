---
title: Enums and match
summary: Types that are one of several variants, possibly carrying data, taken apart with exhaustive match.
order: 7
files: [src/lib.rs]
run: cargo test
hints:
  - "`Shape::area`: `match self { Shape::Circle { radius } => std::f64::consts::PI * radius * radius, Shape::Square(side) => side * side, ... }`."
  - "`value_in_cents` is a `match` with one arm per coin. Leave out an arm and the compiler lists the missing one."
  - "`classify` uses ranges and guards: `0 => \"zero\"`, `1..=9 => \"small\"`, `n if n < 0 => \"negative\"`, `_ => \"large\"`."
  - "`describe(cmd: &Command)`: bind fields in the pattern, `Command::Move { x, y } => format!(\"move to {x},{y}\")`, `Command::Say(text) => format!(\"say {text}\")`."
---

An **enum** is a type whose value is exactly one of a fixed set of variants:

```rust
enum Direction {
    North,
    East,
    South,
    West,
}

let heading = Direction::East;
```

## Variants can carry data

Each variant can hold its own kind of data: nothing, a tuple, or named fields.

```rust
enum Message {
    Quit,
    Write(String),
    Move { x: i32, y: i32 },
    Color(u8, u8, u8),
}

let m = Message::Move { x: 3, y: -1 };
```

This models "one of these shapes of data" directly, where other languages
would need a class hierarchy or a pile of optional fields.

## match

`match` compares a value against patterns, top to bottom, and runs the first
arm that fits. It is an expression, so it produces a value:

```rust
fn turn_right(d: Direction) -> Direction {
    match d {
        Direction::North => Direction::East,
        Direction::East => Direction::South,
        Direction::South => Direction::West,
        Direction::West => Direction::North,
    }
}
```

`match` must be **exhaustive**. Add a fifth direction and every `match` that
forgets it stops compiling, which tells you exactly what to update.

## Pulling data out

Patterns bind the data inside a variant to names:

```rust
fn describe(m: &Message) -> String {
    match m {
        Message::Quit => "quit".to_string(),
        Message::Write(text) => format!("write {text}"),
        Message::Move { x, y } => format!("move {x},{y}"),
        Message::Color(r, g, b) => format!("#{r:02x}{g:02x}{b:02x}"),
    }
}
```

Matching on `&Message` gives you references to the fields, so nothing is
moved out.

## More patterns

```rust
match n {
    0 => "zero",
    1 | 2 | 3 => "a few",           // or
    4..=9 => "several",             // inclusive range
    x if x < 0 => "negative",       // guard: extra condition
    _ => "lots",                    // wildcard: anything else
}
```

## if let

When you only care about one variant, `if let` is shorter than a full `match`:

```rust
if let Message::Write(text) = &m {
    println!("{text}");
}
```

## impl on enums

Enums can have methods just like structs:

```rust
impl Direction {
    fn is_vertical(&self) -> bool {
        matches!(self, Direction::North | Direction::South)
    }
}
```

## Your turn

In `src/lib.rs`:

- `Shape::area()` for each variant (use `std::f64::consts::PI`)
- `value_in_cents(coin)`: penny 1, nickel 5, dime 10, quarter 25
- `classify(n)`: `"negative"`, `"zero"`, `"small"` for 1 to 9, `"large"` above
- `describe(cmd)`: `"move to 3,-1"`, `"say hello"` or `"quit"`
