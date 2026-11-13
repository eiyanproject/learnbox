---
title: Variables and types
summary: let, mut and shadowing; integers, floats, tuples and arrays; converting with as.
order: 2
files: [src/lib.rs]
run: cargo test
hints:
  - "`celsius_to_fahrenheit`: `c * 9.0 / 5.0 + 32.0`. Float literals need the `.0`; `9 / 5` would be integer division."
  - "`seconds_to_hms`: `total / 3600`, then `(total % 3600) / 60`, then `total % 60`. Return them as a tuple `(h, m, s)`."
  - "`average`: convert before dividing, `(a as f64 + b as f64) / 2.0`. Adding two `i32` first could overflow."
  - "`sum_array`: `let mut total = 0; for n in values { total += n; } total`."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **variable** | a name bound to a value with `let` |
| **bind** | give a value a name |
| **immutable** | cannot change; Rust variables are immutable by default |
| **`mut`** | marks a variable that may change |
| **shadowing** | a new `let` with the same name: a new variable, possibly of another type |
| **parse** | turn text into a value, such as a number; it can fail |
| **`unwrap()`** | takes the value out of a result, panicking if it was an error |
| **scalar type** | a single value: an integer, a float, a `bool`, a `char` |
| **signed** / **unsigned** | can be negative (`i32`) / zero and up only (`u8`) |
| **bits** | the number in a type's name: `u8` is 8 bits, 0 to 255 |
| **`usize`** | the type for lengths and indexes |
| **floating point** | `f32`, `f64`: numbers with a fraction |
| **`char`** | one Unicode character, in single quotes |
| **explicit conversion** | Rust never converts numbers silently; use `as` |
| **truncate** | `as i32` drops the fraction, toward zero |
| **integer division** | `/` on integers rounds toward zero: `-7 / 2` is `-3` |
| **remainder** (`%`) | what is left after division |
| **overflow** | a result too big for its type; it panics in a debug build and wraps in a release build |
| **debug** / **release build** | what `cargo run` and `cargo test` make / `cargo build --release`, optimised |
| **tuple** | a fixed group of values of possibly different types: `(1, 2.5)` |
| **destructure** | take a tuple apart: `let (h, m, s) = t;` |
| **array** | a fixed-length list of one type: `[i64; 5]` |
| **`Vec`** | a growable list (Learn lesson 9) |
| **constant** | `const`: a fixed value with a type, in `SCREAMING_SNAKE_CASE` |
| **debug formatting** | `{:?}`, which can print collections |
| **`Option`** | `Some(value)` or `None`, "maybe a value" (Learn lesson 8) |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo test` | what the **Run** button does here: compiles and runs the tests |
| `cargo build --release` | an optimised build, where overflow wraps |

### Rust keywords, types and methods

| Name | What it does |
|---|---|
| `let apples = 5;`, `let mut apples = 5;` | an immutable / a mutable variable |
| `let n: i32 = "42".parse().unwrap();` | text to a number, crashing on bad input |
| `i8`...`i128`, `u8`...`u128`, `isize`, `usize` | integer types |
| `f32`, `f64`, `bool`, `char` | float, true/false, character |
| `x as f64`, `3.9 as i32` | explicit conversions |
| `let t = (1, 2, 5); t.0` | a tuple and its first item |
| `let a = [0; 3];` | an array of three zeros |
| `const MAX_SCORE: u32 = 100;` | a constant |
| `i32::MAX` | the largest `i32` |
| `a.checked_add(b)` | `Some(sum)`, or `None` on overflow |
| `9.0`, `5.0` | float literals need the `.0` |

### Errors

| Error | Means |
|---|---|
| `error[E0384]: cannot assign twice to immutable variable` | changing a variable without `mut` |
| `cannot add f64 to i32` | mixing number types without `as` |
| `attempt to add with overflow` | a debug-build panic on integer overflow |

---

## let and mut

`let` creates a variable. Variables are **immutable** by default: once a
value is bound to a name, it cannot be changed. Trying is a compile error:

```rust
let apples = 5;
apples = 6;         // error: cannot assign twice to immutable variable
```

```text
error[E0384]: cannot assign twice to immutable variable `apples`
  |
2 |     let apples = 5;
  |         ------ first assignment to `apples`
3 |     apples = 6;
  |     ^^^^^^^^^^ cannot assign twice to immutable variable
  |
help: consider making this binding mutable
  |
2 |     let mut apples = 5;
  |         +++
```

The `+++` under `mut` in the `help:` shows exactly what to add. Say so if
you mean to change it:

```rust
let mut apples = 5;
apples += 1;
```

This makes it obvious, when reading code, which values can change, and the
compiler holds you to it: most variables never change, so only the few that
do carry `mut`.

## Shadowing

A new `let` with the same name creates a new variable that hides the old one.
It may even have a different type:

```rust
let input = "42";
let input: i32 = input.parse().unwrap();   // now an i32
```

(A fragment.) `"42"` is text; `parse()` converts it to the type asked for,
here `i32`. Parsing can fail (`"forty"` is not a number), so it returns a
value that is either the number or an error, and `unwrap()` takes the
number out, crashing the program with a message if it was an error. Lesson 8
shows the proper ways to handle that.

Shadowing differs from `mut`: it makes a *new* variable, so the type can
change, and the old value is untouched. `mut` changes the value in place, and
the type can never change. Shadowing is the usual way to convert a value step
by step while keeping one sensible name.

## Scalar types

| Type | What it is |
|---|---|
| `i8` `i16` `i32` `i64` `i128` | signed integers (`i32` is the default) |
| `u8` `u16` `u32` `u64` `u128` | unsigned: zero and up |
| `isize` `usize` | pointer-sized; `usize` is used for lengths and indexes |
| `f32` `f64` | floating point (`f64` is the default) |
| `bool` | `true` / `false` |
| `char` | one Unicode character, in single quotes: `'a'`, `'😀'` |

The number in each name is its size in bits: an `i32` holds about minus to
plus 2.1 billion, a `u8` 0 to 255. Pick by range, and use the defaults when
there is no reason not to. Lengths and positions are always `usize`.

Rust never converts between numeric types silently. `i32 + f64` is a
compile error (``cannot add `f64` to `i32` ``), and so is passing an
`i32` where a `u64` is expected. Other languages convert quietly and
sometimes lose data; Rust makes you say so. Convert explicitly with `as`:

```rust
let count: i32 = 7;
let half = count as f64 / 2.0;   // 3.5
let rounded = 3.9_f64 as i32;    // 3 (truncates toward zero)
```

Integer division rounds toward zero, and `%` is the remainder:

```rust
7 / 2    // 3
7 % 2    // 1
7.0 / 2.0  // 3.5
```

(Expressions with their values.) Unlike Python, `-7 / 2` is `-3`: Rust
rounds toward zero, not down.

In a debug build (what `cargo run` and `cargo test` make), integer overflow
**panics**, which means the program stops with an error message, instead of
silently wrapping. A release build (`cargo build --release`) wraps instead,
for speed, so never rely on either; use the `checked_` methods (below) when
overflow is possible.

## Tuples

A fixed-size group of values of possibly different types:

```rust
let point: (i32, i32) = (3, 4);
let (x, y) = point;       // destructure
let first = point.0;      // or access by position
```

A function can return a tuple to return several values.

## Arrays

A fixed-length list where every item has the same type:

```rust
let days: [&str; 3] = ["Mon", "Tue", "Wed"];
let zeros = [0; 10];        // ten zeros
days[0];                    // "Mon"
days.len();                 // 3
for d in days { println!("{d}"); }
```

Growable lists are `Vec`, which comes later.

## Constants

```rust
const SECONDS_PER_HOUR: u32 = 3600;
```

Constants always need a type, and are written in `SCREAMING_SNAKE_CASE`.

## Run it

```rust
fn main() {
    let input = "42";
    let input: i32 = input.parse().unwrap();
    println!("{}", input + 1);

    let count: i32 = 7;
    println!("{} {}", count as f64 / 2.0, 3.9_f64 as i32);
    println!("{} {} {} {}", 7 / 2, 7 % 2, 7.0 / 2.0, -7 / 2);
    println!("{}", (-3.9_f64) as i32);      // toward zero, not down

    let point = (3, 4);
    let (x, y) = point;
    println!("{x} {y} {}", point.0);

    let days = ["Mon", "Tue", "Wed"];
    println!("{} {} {:?}", days[0], days.len(), [0; 3]);

    println!("{:?}", 250u8.checked_add(10)); // would overflow: None
}
```

```output
43
3.5 3
3 1 3.5 -3
-3
3 4 3
Mon 3 [0, 0, 0]
None
```

Line by line: shadowing turned the text into a number; `as f64` converted
before dividing; `as i32` cut 3.9 down to 3, and -3.9 *up* to -3, both toward
zero. Integer division and remainder, then the tuple taken apart, then the
array (`{:?}` is **debug formatting**, which can print collections; plain
`{}` cannot).

`checked_add` is how you ask for overflow as a value instead of a panic:
250 + 10 does not fit in a `u8`, so it gives `None`, "no result"; a sum that
fits gives `Some(sum)`. Those two are Rust's `Option` type, lesson 8.

## Your turn

The **Run** button here runs `cargo test`, which compiles the project and runs
the (empty) visible tests. It is a fast way to see compile errors.
In `src/lib.rs`:

- `celsius_to_fahrenheit(c)`: `c * 9 / 5 + 32`, with floats (write `9.0`,
  `5.0` and `32.0`: float literals need the `.0`)
- `seconds_to_hms(total)`: split seconds into `(hours, minutes, seconds)`,
  returned as a tuple: 3,725 seconds is `(1, 2, 5)`
- `average(a, b)`: the average of two `i32` values as an `f64`, correct even
  for values near `i32::MAX`. `a + b` in `i32` would overflow there, so
  convert each one to `f64` *before* adding.
- `sum_array(values)`: the sum of a `[i64; 5]`, an array of five `i64`s
