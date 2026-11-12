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

Programs need to choose and to repeat. Rust's tools for both are `if`,
`match` (lesson 7), and three loops: `loop`, `while` and `for`. What sets
them apart from many languages is that `if` and `loop` are **expressions**:
they produce a value, like `a + b` does, so you can assign their result.

## if is an expression

In Rust, `if` produces a value, so there is no separate ternary operator:

```rust
let label = if temperature > 30 { "hot" } else { "fine" };
```

(A fragment.) Each branch is a block whose last expression, with no
semicolon, is that branch's value, the same rule as a function body.

Both branches must produce the same type: `if x { 1 } else { "one" }` is a
compile error, because `label` must have one type whichever branch runs. The
condition must be a `bool`; there is no **truthiness** (treating 0 or empty
values as false, as Python and JavaScript do), so `if count { }` does not
compile (`expected bool, found integer`). Write `if count != 0`.

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

An `if` / `else if` chain runs the **first** branch whose condition holds,
so the order of the checks is part of the logic. FizzBuzz written in the
order the rules are usually stated goes wrong:

```rust
fn fizzbuzz(n: u32) -> String {
    if n % 3 == 0 {
        "Fizz".to_string()
    } else if n % 5 == 0 {
        "Buzz".to_string()
    } else if n % 15 == 0 {              // never reached: 15 already matched % 3
        "FizzBuzz".to_string()
    } else {
        n.to_string()
    }
}

fn main() {
    for n in [3, 5, 15] {
        println!("{n} -> {}", fizzbuzz(n));
    }
}
```

```output
3 -> Fizz
5 -> Buzz
15 -> Fizz
```

15 divides by 3, so the first branch wins and "FizzBuzz" can never be
produced. Put the most demanding condition, divisible by both, first.
`.to_string()` turns a `&str` or a number into an owned `String`, so every
branch has the same type.

## loop

`loop` repeats forever until you `break`. `break` can carry a value out,
which becomes the value of the whole `loop` expression, so a loop can
compute a result and hand it to a `let`:

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

`for` walks anything iterable: each element of an array or vector, each
character of a string, each number in a range. Ranges are the common case:

```rust
for i in 0..5 { }      // 0, 1, 2, 3, 4    (end excluded)
for i in 1..=5 { }     // 1, 2, 3, 4, 5    (end included)
for i in (1..=3).rev() { }   // 3, 2, 1
for i in (0..10).step_by(2) { }
```

(Loop headers with empty bodies.) `a..b` counts from `a` up to but not
including `b`; `a..=b` includes `b`. `.rev()` reverses the order, and
`.step_by(2)` takes every second value.

`for` over a range can never index out of bounds and never loops forever,
which is why it is preferred over `while` with a counter, where forgetting
the `+= 1` or getting the `<` wrong is a common slip.

## Labels

A plain `break` inside nested loops only leaves the innermost one. To break
out of an outer loop from an inner one, give it a **label**, a name starting
with an apostrophe, and break to that name:

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

## Run it

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

fn main() {
    println!("{} {} {}", sign(-5), sign(0), sign(9));

    let mut n = 1;
    let first_big_power = loop {
        n *= 2;
        if n > 1000 {
            break n;
        }
    };
    println!("{first_big_power}");

    println!("{:?}", (0..5).collect::<Vec<_>>());
    println!("{:?}", (1..=5).collect::<Vec<_>>());
    println!("{:?}", (1..=3).rev().collect::<Vec<_>>());
    println!("{:?}", (0..10).step_by(2).collect::<Vec<_>>());

    let mut found = (0, 0);
    'outer: for x in 0..10 {
        for y in 0..10 {
            if x * y == 42 {
                found = (x, y);
                break 'outer;
            }
        }
    }
    println!("{found:?}");
}
```

```output
negative zero positive
1024
[0, 1, 2, 3, 4]
[1, 2, 3, 4, 5]
[3, 2, 1]
[0, 2, 4, 6, 8]
(6, 7)
```

`.collect::<Vec<_>>()` gathers the values of a range into a vector so it can
be printed; iterators and `collect` are lesson 11. The `::<Vec<_>>` part
tells `collect` which kind of collection to build, and `_` lets the compiler
work out the element type. The labelled loop stopped at the first pair whose
product is 42, `(6, 7)`, without trying the rest.

## Your turn

In `src/lib.rs`:

- `fizzbuzz(n)`: `"Fizz"` for multiples of 3, `"Buzz"` for multiples of 5,
  `"FizzBuzz"` for multiples of both, otherwise the number as a `String`
  (mind the order, as above)
- `sum_of_multiples(limit)`: the sum of all numbers **below** `limit` that are
  multiples of 3 or 5 (`sum_of_multiples(10)` is 23: 3 + 5 + 6 + 9)
- `collatz_steps(n)`: steps to reach 1 by halving even numbers and turning odd
  ones into `3n + 1` (`collatz_steps(1)` is 0, `collatz_steps(27)` is 111).
  Parameters are immutable, so shadow it first: `let mut n = n;`
- `is_prime(n)`: `true` for prime numbers. 0 and 1 are not prime, 2 is.
  Trying divisors up to the square root (`d * d <= n`) is enough.
