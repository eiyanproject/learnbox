---
title: Iterators and closures
summary: Chain map, filter and fold instead of writing loops, and pass behaviour around as closures.
order: 11
files: [src/lib.rs]
run: cargo test
hints:
  - "`evens_squared`: `nums.iter().filter(|n| *n % 2 == 0).map(|n| n * n).collect()`."
  - "`count_long_words`: `text.split_whitespace().filter(|w| w.len() >= min_len).count()`."
  - "`running_totals`: keep a `let mut sum = 0;` outside and `.map(|n| { sum += n; sum })`, or use `.scan(0, |acc, &n| { *acc += n; Some(*acc) })`."
  - "`make_adder(n)` returns `impl Fn(i32) -> i32`: `move |x| x + n`. `apply_n`: `let mut x = x; for _ in 0..times { x = f(x); } x`."
---

## Closures

A **closure** is an anonymous function you can store in a variable or pass to
another function:

```rust
let double = |x: i32| x * 2;
double(4);                 // 8

let threshold = 10;
let is_big = |x: i32| x > threshold;   // captures `threshold` from outside
```

Types are usually inferred. A multi-line body uses braces:
`|x| { let y = x + 1; y * y }`.

`move |x| ...` makes the closure take ownership of what it captures. You need
it when the closure outlives the scope it was created in, such as when a
function returns it.

## Iterators

An **iterator** produces a sequence of values, one at a time. Collections give
you one:

```rust
let v = vec![1, 2, 3];
v.iter()          // yields &i32   (borrows)
v.iter_mut()      // yields &mut i32
v.into_iter()     // yields i32    (consumes v)
"a b".split_whitespace()   // yields &str
(1..=5)                    // ranges are iterators
```

## Adapters are lazy

`map`, `filter` and friends build a new iterator; nothing runs until
something **consumes** it:

```rust
let squares: Vec<i32> = (1..=5)
    .filter(|n| n % 2 == 1)
    .map(|n| n * n)
    .collect();          // [1, 9, 25]
```

Common adapters: `map`, `filter`, `enumerate`, `zip`, `rev`, `skip`, `take`,
`chain`, `flat_map`, `scan`.

Common consumers: `collect`, `sum`, `count`, `min`, `max`, `fold`, `any`,
`all`, `find`, `position`, `for_each`.

`collect` needs to know what to build. Annotate the variable, or use the
turbofish: `.collect::<Vec<_>>()`. It can also build a `String`, a `HashMap`
or a `HashSet`.

## References in closures

`v.iter()` yields `&i32`, and `filter` hands its closure a reference to
*that*, so the closure sees `&&i32`. Patterns or `*` peel the layers off:

```rust
v.iter().filter(|&&n| n > 1)
v.iter().filter(|n| **n > 1)
v.iter().copied().filter(|n| *n > 1)   // copied() turns &i32 into i32 first
```

The compiler's error message tells you which one it expects.

## fold

`fold` carries a running value through the sequence:

```rust
let product = (1..=5).fold(1, |acc, n| acc * n);   // 120
```

## Functions that take closures

Use a trait bound. `Fn` can be called many times without changing anything it
captured; `FnMut` may change captured state; `FnOnce` may be called once.

```rust
fn twice<F: Fn(i32) -> i32>(f: F, x: i32) -> i32 {
    f(f(x))
}
twice(|n| n + 3, 1);    // 7
```

Return one with `impl Fn(...)`.

## Run it

```rust
fn twice<F: Fn(i32) -> i32>(f: F, x: i32) -> i32 {
    f(f(x))
}

fn make_adder(n: i32) -> impl Fn(i32) -> i32 {
    move |x| x + n
}

fn main() {
    let double = |x: i32| x * 2;
    let threshold = 10;
    let is_big = |x: i32| x > threshold;
    println!("{} {} {}", double(4), is_big(11), is_big(3));

    let squares: Vec<i32> = (1..=5).filter(|n| n % 2 == 1).map(|n| n * n).collect();
    println!("{squares:?}");

    let v = vec![1, 2, 3];
    let a: Vec<_> = v.iter().filter(|&&n| n > 1).collect();
    let b: Vec<_> = v.iter().copied().filter(|n| *n > 1).collect();
    println!("{a:?} {b:?}");

    println!("{}", (1..=5).fold(1, |acc, n| acc * n));
    println!("{} {}", twice(|n| n + 3, 1), make_adder(10)(5));

    let mut seen = Vec::new();
    let lazy = (1..=3).map(|n| {
        seen.push(n);
        n * 10
    });
    let first: Vec<i32> = lazy.take(2).collect();
    println!("{first:?} {seen:?}");
}
```

```output
8 true false
[1, 9, 25]
[2, 3] [2, 3]
120
7 15
[10, 20] [1, 2]
```

The last line is laziness made visible: `take(2)` asked for two values, so the closure ran twice and never saw `3`.

## Your turn

In `src/lib.rs`, preferably with iterator chains rather than `for` loops:

- `evens_squared(nums)`: squares of the even numbers, in order
- `count_long_words(text, min_len)`: how many words have at least `min_len` bytes
- `running_totals(nums)`: `[1, 2, 3]` becomes `[1, 3, 6]`
- `make_adder(n)`: returns a closure that adds `n` to its argument
- `apply_n(f, times, x)`: calls `f` on `x`, `times` times over
