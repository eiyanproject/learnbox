---
title: Option and Result
summary: No null, no exceptions. Model "maybe missing" and "might fail" in the type, and propagate errors with ?.
order: 8
files: [src/lib.rs]
run: cargo test
hints:
  - "`find_index`: loop with `for (i, item) in items.iter().enumerate()`; `return Some(i)` on a match; `None` after the loop."
  - "`parse_age`: `let n: i64 = s.trim().parse().map_err(|_| format!(\"not a number: {}\", s.trim()))?;` then check `0..=150` and return `Ok(n as u8)`."
  - "`add_strings` returns the same error type as `parse`, so `?` can pass it straight up: `Ok(a.trim().parse::<i64>()? + b.trim().parse::<i64>()?)`."
  - "`safe_divide(a, b)`: `if b == 0 { None } else { Some(a / b) }`, or use `a.checked_div(b)`."
---

Two questions come up in almost every program: "what if there is nothing
there?" (no user with that name, no even number in the list) and "what if it
fails?" (the text is not a number, the file does not exist).

Many languages answer the first with **null**: a special value meaning
"nothing", which every reference might secretly be. Forget to check for it
and the program crashes, at run time, wherever the null finally gets used.
Tony Hoare, who introduced null in 1965, later called it his "billion-dollar
mistake". The second question is usually answered with **exceptions**, which
jump out of the function, invisible in its signature, so a reader cannot
tell which calls may fail.

Rust has neither. Instead, two ordinary enums from the standard library,
built exactly like the enums of the last lesson, make "might be missing" and
"might fail" part of a function's **type**. The caller can see them in the
signature, and the compiler will not let them forget.

## Option

```rust
enum Option<T> {
    Some(T),
    None,
}
```

(This is how the standard library defines it; you do not write it
yourself.) The `<T>` means `Option` works for any type `T`: an
`Option<i32>` holds either `Some(an i32)` or `None`, an `Option<String>`
either `Some(a String)` or `None`. (Writing such generic types yourself is
lesson 12.) `Option`, `Some` and `None` are so common that they are always
in scope; you write `Some(3)`, not `Option::Some(3)`.

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

(`for &n in nums` takes each `&i32` the slice gives and copies the number out
of it, so `n` is a plain `i32`.)

An `Option<i32>` is **not** an `i32`, and that is the whole point. You cannot
use it as a number until you have dealt with the `None` case:

```rust
let n = first_even(&[1, 3, 4]);
let doubled = n * 2;      // error[E0369]: cannot multiply `Option<i32>` by `{integer}`
```

With null, `n * 2` would compile and fail on the day the list had no even
number. Here it cannot compile, so that day never comes.

## Result

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

`Result` is for operations that can fail. `Ok` holds the value of type `T`
on success; `Err` holds an error of type `E` saying what went wrong. Unlike
`None`, an `Err` carries information. For example, `"42".parse::<i32>()`
returns `Result<i32, ParseIntError>`:

```rust
match "42".parse::<i32>() {
    Ok(n) => println!("{n}"),
    Err(e) => println!("bad number: {e}"),
}
```

(`parse::<i32>()` names the target type directly; this `::<...>` syntax is
the same one `collect` used in lesson 3.) A `ParseIntError` prints as a
human-readable reason, such as `invalid digit found in string`.

## Taking the value out: unwrap and expect

The quickest way to get the value out is `unwrap()`: it gives the value
inside `Some` or `Ok`, and on `None` or `Err` it **panics**, stopping the
program:

```rust
fn main() {
    let n: i32 = "x".parse().unwrap();
    println!("{n}");
}
```

```text
thread 'main' (4242) panicked at src/main.rs:2:30:
called `Result::unwrap()` on an `Err` value: ParseIntError { kind: InvalidDigit }
```

The panic message says which thread failed (the number in brackets is its
ID, different on every run), where (`src/main.rs`, line 2, column 30) and why (it
prints the `Err` value in debug form). `expect("message")` does the same but
puts your own message first, so `.expect("age must be a number")` explains
the failure in words.

`unwrap` and `expect` are fine in tests, in quick experiments, and where a
failure would really be a bug in your own program. For anything that can
happen in normal use (a user typing text instead of a number), crashing is
the wrong answer: handle it with `match`, the helpers below, or `?`.

## Handy methods

Both types have many helpers, so you rarely need a full `match`:

```rust
opt.unwrap_or(0)              // the value, or 0 if None
opt.is_some()   opt.is_none() // ask which variant it is
opt.map(|n| n * 2)            // Some(5) becomes Some(10); None stays None
res.unwrap_or_default()       // the value, or the type's default (0, "", ...)
res.ok()                      // Result to Option: Ok(v) to Some(v), Err to None
res.map_err(|e| e.to_string())   // change the error, keep the Ok value
```

(Calls on some `opt: Option<i32>` and `res: Result<i32, ...>`.) `|n| n * 2`
is a **closure**: a small function written inline, taking `n` and returning
`n * 2`. Closures get a lesson of their own (11); for now, read `|x| expr` as
"given `x`, produce `expr`".

## The ? operator

A function that does several steps that can fail would need a `match` for
each one. Here is one step, written out in full:

```rust
use std::num::ParseIntError;

fn double_string(s: &str) -> Result<i32, ParseIntError> {
    let n: i32 = match s.parse() {
        Ok(v) => v,
        Err(e) => return Err(e),    // give up, and hand the error to our caller
    };
    Ok(n * 2)
}
```

That `match`, "give me the value, or return the error", is so common that it
has its own operator. `?` after a `Result` means exactly that:

```rust
fn double_string(s: &str) -> Result<i32, ParseIntError> {
    let n: i32 = s.parse()?;     // on Err, double_string returns that Err now
    Ok(n * 2)
}
```

On `Ok(v)`, the expression `s.parse()?` is `v`. On `Err(e)`, the function
returns `Err(e)` immediately, and the lines below never run. The error
**propagates** (is passed up) to the caller, who can deal with it or pass it
up again with their own `?`.

The full version is a little more than the `match` above: `?` returns
`Err(From::from(e))`, converting the error to the function's error type when
a conversion is defined. When none is, you get an error like this one, from
a function returning `Result<i32, String>`:

```text
error[E0277]: `?` couldn't convert the error to `String`
  |
2 | fn f(s: &str) -> Result<i32, String> {
  |                  ------------------- expected `String` because of this
3 |     let n: i32 = s.parse()?;
  |                  ---------^ the trait `From<ParseIntError>` is not implemented for `String`
  |                  |
  |                  this can't be annotated with `?` because it has type `Result<_, ParseIntError>`
  |
  = note: the question mark operation (`?`) implicitly performs a conversion on the error value using the `From` trait
```

The fix is to convert the error yourself before the `?`:
`s.parse().map_err(|e: ParseIntError| e.to_string())?`, or with your own
message, `map_err(|_| format!("not a number: {s}"))?`. (`From` is a trait,
lesson 10; the intermediate error-handling lesson builds on this.)

Two more rules:

- `?` only works inside a function that itself returns `Result` (or
  `Option`), because it needs somewhere to return the error to. Used in a
  function returning `()` or `i32`, it is a compile error.
- `?` works on `Option` too, in a function returning `Option`: `None` is
  returned early, `Some(v)` gives `v`.

## Run it

```rust
use std::num::ParseIntError;

fn first_even(nums: &[i32]) -> Option<i32> {
    for &n in nums {
        if n % 2 == 0 {
            return Some(n);
        }
    }
    None
}

fn double_string(s: &str) -> Result<i32, ParseIntError> {
    let n: i32 = s.parse()?;
    Ok(n * 2)
}

fn main() {
    println!("{:?} {:?}", first_even(&[1, 3, 4]), first_even(&[1, 3]));
    match "4x".parse::<i32>() {
        Ok(n) => println!("{n}"),
        Err(e) => println!("bad number: {e}"),
    }

    let opt: Option<i32> = None;
    println!("{} {:?}", opt.unwrap_or(0), Some(5).map(|n| n * 2));
    println!("{:?} {:?}", double_string("21"), double_string("x").map_err(|e| e.to_string()));

    let res: Result<i32, String> = Err("nope".into());
    println!("{:?} {}", res.clone().ok(), res.unwrap_or_default());
}
```

```output
Some(4) None
bad number: invalid digit found in string
0 Some(10)
Ok(42) Err("invalid digit found in string")
None 0
```

Line by line: `[1, 3]` has no even number, so `None`; `"4x"` failed to
parse and the `Err` arm printed the reason; `unwrap_or` supplied the 0 for
`None`; `double_string("x")` returned early at the `?`, and `map_err` turned
its `ParseIntError` into a `String`; finally, `.ok()` of an `Err` is `None`,
and the default for `i32` is 0. (`.clone()` is there because `.ok()` takes
the `Result` by value, and the next call still needs it.)

## Your turn

In `src/lib.rs`:

- `find_index(items, target)`: the position of the first item equal to
  `target`, as `Some(position)`, or `None` if it is not there
- `parse_age(s)`: turn text into an age as `Result<u8, String>`:
  - ignore whitespace around the number: `" 7\n"` is `Ok(7)`;
  - text that is not a whole number gives `Err("not a number: <text>")`, for
    example `"not a number: forty"` and `"not a number: 4.5"`;
  - a whole number outside 0 to 150 gives `Err("out of range: <n>")`: both
    `"151"` and `"-3"` are out of range, not "not a number". Parse into a
    signed type wide enough for both, such as `i64`, then check the range.
- `add_strings(a, b)`: parse both (ignoring surrounding whitespace) as `i64`
  and return their sum, passing any `ParseIntError` up unchanged with `?`:
  `add_strings("1", "two")` returns the very error `"two".parse::<i64>()`
  gives
- `safe_divide(a, b)`: `Some(a / b)`, or `None` when `b` is 0
