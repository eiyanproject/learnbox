---
title: Control flow
summary: if as an expression, loop, while and for over ranges, and returning values out of loops.
order: 3
files: [src/lib.rs]
run: cargo test
hints:
  - "`fizzbuzz` can be one `if / else if / else` chain used as the function's final expression. The number case is `n.to_string()`."
  - "`sum_of_multiples`: `for n in 1..limit { if n % 3 == 0 || n % 5 == 0 { total += n; } }`."
  - "`collatz_steps` takes `n: u64` by value, so you can shadow it as mutable: `let mut n = n;` then `while n != 1 { ... }`."
  - "`is_prime`: numbers below 2 are not prime. Otherwise try divisors from 2 while `d * d <= n`; return `false` as soon as one divides evenly."
---

## if is an expression

In Rust, `if` produces a value, so there is no separate ternary operator:

```rust
let label = if temperature > 30 { "hot" } else { "fine" };
```

Both branches must produce the same type. The condition must be a `bool`;
there is no truthiness, so `if count { }` does not compile. Write `if count != 0`.

```rust
fn sign(n: i32) -> &'static str {
    if n < 0 {
        "negative"
    } else if n == 0 {
        "zero"
    } else {
        "positive"
    }
}
```

The whole `if` is the last expression of the function, so its value is
returned. (`&'static str` is a string literal's type; the lifetime lesson
explains `'static`.)

## loop

`loop` repeats forever until you `break`. `break` can carry a value out:

```rust
let mut n = 1;
let first_big_power = loop {
    n *= 2;
    if n > 1000 {
        break n;       // the loop evaluates to 1024
    }
};
```

## while

```rust
let mut countdown = 3;
while countdown > 0 {
    println!("{countdown}");
    countdown -= 1;
}
```

## for and ranges

`for` walks anything iterable. Ranges are the common case:

```rust
for i in 0..5 { }      // 0, 1, 2, 3, 4    (end excluded)
for i in 1..=5 { }     // 1, 2, 3, 4, 5    (end included)
for i in (1..=3).rev() { }   // 3, 2, 1
for i in (0..10).step_by(2) { }
```

`for` over a range can never index out of bounds and never loops forever,
which is why it is preferred over `while` with a counter.

## Labels

To break out of an outer loop from an inner one, name it:

```rust
'outer: for x in 0..10 {
    for y in 0..10 {
        if x * y == 42 {
            break 'outer;
        }
    }
}
```

## Parameters are immutable too

A parameter behaves like a `let` binding. To change it inside the function,
shadow it: `let mut n = n;`.

## Your turn

In `src/lib.rs`:

- `fizzbuzz(n)`: `"Fizz"` for multiples of 3, `"Buzz"` for 5, `"FizzBuzz"` for
  both, otherwise the number as a `String`
- `sum_of_multiples(limit)`: the sum of all numbers **below** `limit` that are
  multiples of 3 or 5 (`sum_of_multiples(10)` is 23)
- `collatz_steps(n)`: steps to reach 1 by halving even numbers and turning odd
  ones into `3n + 1` (`collatz_steps(1)` is 0, `collatz_steps(27)` is 111)
- `is_prime(n)`
