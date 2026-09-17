---
title: Option and Result
summary: No null, no exceptions. Model "maybe missing" and "might fail" in the type, and propagate errors with ?.
order: 8
files: [src/lib.rs]
run: cargo test
hints:
  - "`find_index`: loop with `for (i, item) in items.iter().enumerate()`; `return Some(i)` on a match; `None` after the loop."
  - "`parse_age`: `let n: u32 = s.trim().parse().map_err(|_| format!(\"not a number: {s}\"))?;` then check the range and return `Ok(n as u8)`."
  - "`add_strings` returns the same error type as `parse`, so `?` can pass it straight up: `Ok(a.trim().parse::<i64>()? + b.trim().parse::<i64>()?)`."
  - "`safe_divide(a, b)`: `if b == 0 { None } else { Some(a / b) }`, or use `a.checked_div(b)`."
---

Rust has no `null` and no exceptions. Instead, two ordinary enums from the
standard library make "might be missing" and "might fail" part of a
function's type, so callers cannot forget to deal with them.

## Option

```rust
enum Option<T> {
    Some(T),
    None,
}
```

```rust
fn first_even(nums: &[i32]) -> Option<i32> {
    for &n in nums {
        if n % 2 == 0 {
            return Some(n);
        }
    }
    None
}

match first_even(&[1, 3, 4]) {
    Some(n) => println!("found {n}"),
    None => println!("no even numbers"),
}
```

An `Option<i32>` is not an `i32`. You cannot add 1 to it until you have
handled the `None` case.

## Result

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

`"42".parse::<i32>()` returns `Result<i32, ParseIntError>`:

```rust
match "42".parse::<i32>() {
    Ok(n) => println!("{n}"),
    Err(e) => println!("bad number: {e}"),
}
```

## Handy methods

Both types have many helpers, so you rarely need a full `match`:

```rust
opt.unwrap_or(0)              // value, or a default
opt.is_some()   opt.is_none()
opt.map(|n| n * 2)            // transform the value inside, if any
res.unwrap_or_default()
res.ok()                      // Result -> Option, dropping the error
res.map_err(|e| e.to_string())   // change the error type
```

`unwrap()` and `expect("message")` take the value out and **panic** if there
is none. They are fine in tests and quick experiments, and a smell in real
code paths.

## The ? operator

Writing `match` for every step that can fail gets long. `?` does it for you:
on `Ok(v)` it gives `v`; on `Err(e)` it **returns** `Err(e)` from the
enclosing function immediately.

```rust
use std::num::ParseIntError;

fn double_string(s: &str) -> Result<i32, ParseIntError> {
    let n: i32 = s.parse()?;     // early-returns the error if parsing fails
    Ok(n * 2)
}
```

The error type must match the function's return type (or be convertible to
it). If it does not, convert it with `map_err` first. `?` works on `Option`
in functions returning `Option` too.

## Your turn

In `src/lib.rs`:

- `find_index(items, target)`: the position of `target`, or `None`
- `parse_age(s)`: parse text (ignoring surrounding whitespace) into an age
  from 0 to 150. Errors are `String`s: `"not a number: <input>"` when it does
  not parse as a whole number, and `"out of range: <n>"` otherwise.
- `add_strings(a, b)`: parse both and add them, passing any `ParseIntError`
  up with `?`
- `safe_divide(a, b)`: `None` when dividing by zero
