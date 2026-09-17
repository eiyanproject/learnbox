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

## let and mut

Variables are **immutable** by default:

```rust
let apples = 5;
apples = 6;         // error: cannot assign twice to immutable variable
```

Say so if you mean to change it:

```rust
let mut apples = 5;
apples += 1;
```

This makes it obvious, when reading code, which values can change.

## Shadowing

A new `let` with the same name creates a new variable that hides the old one.
It may even have a different type:

```rust
let input = "42";
let input: i32 = input.parse().unwrap();   // now an i32
```

## Scalar types

| Type | What it is |
|---|---|
| `i8` `i16` `i32` `i64` `i128` | signed integers (`i32` is the default) |
| `u8` `u16` `u32` `u64` `u128` | unsigned: zero and up |
| `isize` `usize` | pointer-sized; `usize` is used for lengths and indexes |
| `f32` `f64` | floating point (`f64` is the default) |
| `bool` | `true` / `false` |
| `char` | one Unicode character, in single quotes: `'a'`, `'😀'` |

Rust never converts between numeric types silently. `i32 + f64` is a
compile error. Convert explicitly with `as`:

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

In a debug build, integer overflow panics instead of silently wrapping.

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

## Your turn

The **Run** button here runs `cargo test`, which compiles the project and runs
the (empty) visible tests. It is a fast way to see compile errors.
In `src/lib.rs`:

- `celsius_to_fahrenheit(c)`: `c * 9 / 5 + 32`, with floats
- `seconds_to_hms(total)`: split seconds into `(hours, minutes, seconds)`
- `average(a, b)`: the average of two `i32` values as an `f64`, correct even
  for values near `i32::MAX`
- `sum_array(values)`: the sum of a `[i64; 5]`
