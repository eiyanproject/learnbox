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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **enum** (enumeration) | an "or" type: a value is exactly one of a fixed list of variants |
| **variant** | one of an enum's possibilities, named `Direction::East` |
| **variant data** | what a variant carries: nothing, a tuple of values, or named fields |
| **`match`** | compares a value with patterns, top to bottom, and runs the first that fits |
| **pattern** | the shape a value is tested against: a variant, a number, a range, `_` |
| **arm** | one `pattern => expression` pair; arms are separated by commas |
| **exhaustive** | covering every possible value; a `match` must be |
| **binding** | a pattern giving names to the data inside: `Message::Move { x, y }` |
| **matching on a reference** | gives references to the fields, so nothing is moved out |
| **wildcard** (`_`) | matches anything; usually the last arm |
| **or-pattern** (`\|`) | `1 \| 2 \| 3`: any of these |
| **range pattern** | `4..=9`: from 4 to 9 inclusive |
| **guard** | `x if x < 0`: an extra condition on an arm |
| **unreachable pattern** | an arm that can never run because an earlier one catches everything |
| **`if let`** | runs a block only if a value fits one pattern; not exhaustive |
| **hexadecimal** | base 16; `{r:02x}` prints two hex digits with a leading zero |
| **π** | the circle constant, `std::f64::consts::PI` |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo test` | compiles and runs the tests |

### Rust names

| Name | What it does |
|---|---|
| `enum Direction { North, East, South, West }` | an enum with four variants |
| `enum Message { Quit, Write(String), Move { x: i32, y: i32 } }` | variants carrying data |
| `match d { Direction::North => 0, ... }` | a match expression |
| `Message::Write(text) => ...` | binds `text` to the variant's data |
| `x if x < 0 => "negative"` | an arm with a guard |
| `_ => "lots"` | the catch-all arm |
| `if let Message::Write(text) = &m { ... } else { ... }` | handle one variant |
| `impl Direction { fn ...(&self) }` | methods on an enum |
| `matches!(value, pattern)` | `true` if the value fits the pattern |
| `format!("move to {x},{y}")` | builds the description |
| `radius * radius`, `r.powi(2)` | squaring |

### Errors

| Error | Means |
|---|---|
| `error[E0004]: non-exhaustive patterns: Direction::West not covered` | a `match` misses a variant |
| `patterns i32::MIN..=-1_i32 ... not covered` | a number `match` without a final `_` |
| `warning: unreachable pattern` | an arm after one that already catches everything |

---

A struct says "a user has a name **and** an age **and** an active flag". Many
things are the other way round: a direction is north **or** east **or** south
**or** west; a network message is a quit **or** a text **or** a move. An
**enum** (short for enumeration) is that "or" type: a value of an enum is
exactly one of a fixed list of **variants**, never two at once and never
something outside the list.

```rust
enum Direction {
    North,
    East,
    South,
    West,
}

let heading = Direction::East;
```

(A fragment.) Variants are named with the enum's name and `::`, as in
`Direction::East`, the same `::` used for associated functions.

Why not use numbers, 0 for north, 1 for east and so on? Because then `7` is
also a "direction", nothing stops you from passing a direction where a day
of the week was wanted, and the reader has to remember which number means
what. With an enum, the compiler knows the complete list, and as you will see
below, it uses that list to check your code.

## Variants can carry data

Each variant can hold its own kind of data: nothing, a tuple of values, or
named fields like a struct.

```rust
enum Message {
    Quit,                         // no data
    Write(String),                // one unnamed value
    Move { x: i32, y: i32 },      // named fields
    Color(u8, u8, u8),            // three unnamed values
}

let m = Message::Move { x: 3, y: -1 };
let w = Message::Write(String::from("hi"));
```

A `Message` is always one of the four, and only a `Move` has an `x`. In a
language without such enums you would write either a class hierarchy (a
`Message` base class with four subclasses) or one class with every field,
most of them left empty depending on the kind. An enum states the real
shape: each kind of message carries exactly its own data.

## match

`match` compares a value against **patterns**, top to bottom, and runs the
first **arm** (a `pattern => expression` pair) that fits. Like `if`, it is an
expression, so the arm that runs produces the value of the whole `match`:

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

Arms are separated by commas. An arm that needs several statements uses a
block: `Direction::North => { println!("turning"); Direction::East }`.

## match must be exhaustive

A `match` has to cover **every** possible value. Forget a variant and the
code does not compile. Here `West` is missing:

```rust
fn degrees(d: Direction) -> i32 {
    match d {
        Direction::North => 0,
        Direction::East => 90,
        Direction::South => 180,
        // Direction::West => 270,    // uncomment to fix
    }
}
```

```text
error[E0004]: non-exhaustive patterns: `Direction::West` not covered
 --> src/lib.rs:3:11
  |
3 |     match d {
  |           ^ pattern `Direction::West` not covered
  |
note: `Direction` defined here
 --> src/lib.rs:1:10
  |
1 | pub enum Direction { North, East, South, West }
  |          ^^^^^^^^^                       ---- not covered
  = note: the matched value is of type `Direction`
help: ensure that all possible cases are being handled by adding a match arm with a wildcard pattern or an explicit pattern as shown
  |
6 ~         Direction::South => 180,
7 ~         Direction::West => todo!(),
  |
```

Reading it: the `^` points at the `match`; the `note:` shows the enum's
definition with the forgotten variant underlined; the `help:` shows the arm
to add, with `todo!()` as a placeholder body (`todo!()` panics if it is ever
reached, so it is a reminder, not a fix).

This is the main reason to use enums. Add a fifth variant to an enum months
later, and every `match` anywhere in the program that does not handle it
stops compiling, each one listed with its file and line. In languages
without this check, the new case falls silently into some default branch,
and you find out from a bug report.

## Pulling data out

A pattern can do more than recognise a variant: it can give names to the
data inside, which is called **binding**. The names exist only inside that
arm:

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

Step by step, for `describe(&Message::Move { x: 3, y: -1 })`:

1. `Message::Quit` does not fit: the value is a `Move`.
2. `Message::Write(text)` does not fit either.
3. `Message::Move { x, y }` fits; `x` is bound to 3 and `y` to -1.
4. That arm's expression, `format!("move {x},{y}")`, is the result:
   `"move 3,-1"`. The last arm is never looked at.

`describe` takes `&Message`, a reference, so it only borrows the message.
Matching on a reference gives **references** to the fields too (`text` is a
`&String`), so nothing is moved out, and the caller still has the whole
message afterwards. Had it taken `m: Message`, the `String` inside a `Write`
would have been moved into `text`.

In the `Color` arm, `{r:02x}` is a format specification: `x` prints the
number in hexadecimal (base 16), and `02` pads it to two digits with a
leading zero, so 255, 128, 0 becomes `ff8000`.

## More patterns

Patterns are not only for enums. They work on numbers, characters, tuples and
more:

```rust
match n {
    0 => "zero",                    // one exact value
    1 | 2 | 3 => "a few",           // |  means "or"
    4..=9 => "several",             // an inclusive range
    x if x < 0 => "negative",       // a guard: bind x, then also require x < 0
    _ => "lots",                    // _ matches anything: the "everything else" arm
}
```

(A fragment, with `n: i32`.) Two things to know:

- **Order matters**, as with `if` / `else if`: the first fitting arm wins. Put
  `_ => "lots"` first and every other arm is dead; the compiler warns
  `unreachable pattern`.
- Exhaustiveness still applies. An `i32` has about four billion values, and
  the arms above only list a few of them, so without the final `_` the match
  would not compile (``patterns `i32::MIN..=-1_i32` and `10_i32..=i32::MAX`
  not covered``). The compiler does not reason about guards, so even though
  `x if x < 0` covers all negative numbers, it still needs the `_`.

## if let

Often you care about only one variant and want to ignore the rest. A full
`match` for that needs a do-nothing `_ => {}` arm:

```rust
match &m {
    Message::Write(text) => println!("{text}"),
    _ => {}
}
```

`if let` says the same thing in less space:

```rust
if let Message::Write(text) = &m {
    println!("{text}");
}
```

Read it as "if `&m` fits the pattern `Message::Write(text)`, bind `text` and
run the block". It may have an `else` for when it does not fit. The cost of
the shorter form: it is not exhaustive, so the compiler will not tell you
about variants you forgot. Use `match` when every case needs handling.

## impl on enums

Enums can have methods, exactly like structs:

```rust
impl Direction {
    fn is_vertical(&self) -> bool {
        matches!(self, Direction::North | Direction::South)
    }
}
```

`matches!(value, pattern)` is a shorthand that is `true` when the value fits
the pattern and `false` otherwise, the same as
`match self { Direction::North | Direction::South => true, _ => false }`.

## Run it

```rust
enum Message {
    Quit,
    Write(String),
    Move { x: i32, y: i32 },
    Color(u8, u8, u8),
}

fn describe(m: &Message) -> String {
    match m {
        Message::Quit => "quit".to_string(),
        Message::Write(text) => format!("write {text}"),
        Message::Move { x, y } => format!("move {x},{y}"),
        Message::Color(r, g, b) => format!("#{r:02x}{g:02x}{b:02x}"),
    }
}

fn size(n: i32) -> &'static str {
    match n {
        0 => "zero",
        1 | 2 | 3 => "a few",
        4..=9 => "several",
        x if x < 0 => "negative",
        _ => "lots",
    }
}

fn main() {
    let msgs = [
        Message::Quit,
        Message::Write("hi".to_string()),
        Message::Move { x: 3, y: -1 },
        Message::Color(255, 128, 0),
    ];
    for m in &msgs {
        println!("{}", describe(m));
    }
    for n in [0, 2, 7, -4, 50] {
        print!("{} ", size(n));
    }
    println!();
    if let Message::Write(text) = &msgs[1] {
        println!("{text}");
    }
}
```

```output
quit
write hi
move 3,-1
#ff8000
zero a few several negative lots 
hi
```

`for m in &msgs` borrows each message (lesson 4), so `msgs` is still there
for the `if let` at the end. `-4` went past `0`, `1 | 2 | 3` and `4..=9`, and
was caught by the guard; `50` fit nothing but `_`.

## Your turn

In `src/lib.rs`:

- `Shape::area()` for each variant: a `Circle` is π × radius² (use
  `std::f64::consts::PI`), a `Square` is side², a `Rectangle` is width ×
  height
- `value_in_cents(coin)`: penny 1, nickel 5, dime 10, quarter 25
- `classify(n)`: `"negative"` below 0, `"zero"`, `"small"` for 1 to 9 inclusive,
  `"large"` for 10 and above
- `describe(cmd)`: exactly `"move to 3,-1"` for `Move { x: 3, y: -1 }` (no
  space after the comma), `"say hello"` for `Say("hello")`, and `"quit"`

`describe` takes `&Command`, so the `String` inside `Say` arrives as a
`&String`; `format!` can use it as it is.
