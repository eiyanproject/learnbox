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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **iterator chain** | steps like `filter`, `map`, `collect` joined with dots |
| **closure** | a function without a name, written inline: `\|n\| n * 2` |
| **capture** | a closure using variables from the code around it |
| **`Fn`** | only reads what it captured, by `&`; callable any number of times |
| **`FnMut`** | changes what it captured, by `&mut`; needs `mut` to call |
| **`FnOnce`** | moves what it captured away; callable once |
| **`move`** | makes a closure take its captured variables by value |
| **outlive** | live longer than; a returned closure outlives the function's parameters |
| **`impl Fn(i32) -> i32`** | "some closure taking and returning an `i32`", as a type |
| **iterator** | produces values one at a time; defined by the `Iterator` trait |
| **`next`** | the one required method: `Some(value)`, then `None` when finished |
| **`while let`** | `if let` in a loop: keep going while the pattern fits |
| **`iter`**, **`iter_mut`**, **`into_iter`** | iterate by `&`, by `&mut`, or by value (consuming the collection) |
| **adapter** | returns a new iterator: `map`, `filter`, `enumerate`, `zip`, `take`, `skip`, `rev`, `chain`, `flat_map`, `scan` |
| **consumer** | pulls every value through: `collect`, `sum`, `count`, `min`, `max`, `fold`, `any`, `all`, `find`, `position`, `for_each` |
| **lazy** | adapters do nothing until a consumer asks for values |
| **`&&i32`** | a reference to a reference, as `filter` gives after `iter()` |
| **accumulator** | the running value `fold` carries through |
| **running total** | each item is the sum of everything up to it |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo test` | compiles and runs the tests |

### Rust names

| Name | What it does |
|---|---|
| `let add = \|a, b\| a + b;` | a closure in a variable |
| `fn apply<F: Fn(i32) -> i32>(f: F, x: i32) -> i32` | a function that takes a closure |
| `move \|x\| x + n` | a closure owning its copy of `n` |
| `(1..=5).filter(\|n\| n % 2 == 1).map(\|n\| n * n).collect::<Vec<_>>()` | the chain from the start |
| `.filter(\|&&n\| n > 1)`, `.filter(\|n\| **n > 1)`, `.copied()` | ways to peel off references |
| `.fold(1, \|acc, n\| acc * n)` | a product with an accumulator |
| `.scan(0, \|sum, &n\| { *sum += n; Some(*sum) })` | running totals |
| `text.split_whitespace()`, `s.chars()` | iterators over words; characters |
| `drop(x)` | drops a value on the spot |

### Errors

| Error | Means |
|---|---|
| `error[E0373]: closure may outlive the current function, but it borrows n` | a returned closure needs `move` |
| `warning: unused Map that must be used` / `iterators are lazy and do nothing unless consumed` | a chain with no consumer |
| `error[E0308]: mismatched types ... expected &&i32, found integer` | comparing a reference with a number |
| `cannot borrow count as mutable` | an `FnMut` closure called without `mut` |

---

Here is a loop that collects the squares of the odd numbers from 1 to 5:

```rust
let mut squares = Vec::new();
for n in 1..=5 {
    if n % 2 == 1 {
        squares.push(n * n);
    }
}
```

And here is the same thing as an **iterator chain**:

```rust
let squares: Vec<i32> = (1..=5).filter(|n| n % 2 == 1).map(|n| n * n).collect();
```

The chain reads as a sentence: from 1 to 5, keep the odd ones, square them,
collect them. There is no mutable vector, no `push`, and no index to get
wrong. Rust programmers write this style all the time, and it compiles to
code as fast as the loop. It needs two ideas: **closures**, the small
functions in `|n| ...`, and **iterators**, the things that produce values one
by one. Closures first.

## Closures

A **closure** is a function without a name, written inline, that you can
store in a variable or pass to another function:

```rust
let double = |x: i32| x * 2;
double(4);                 // 8
```

(Fragments, with the value as a comment.) The parameters go between `|` bars
and the body follows. Compare it with the function it stands for:

```rust
fn double(x: i32) -> i32 { x * 2 }
let double = |x: i32| x * 2;
let double = |x| x * 2;          // types worked out from how it is used
let double = |x| { let y = x * 2; y };   // a block for several statements
```

Unlike a `fn`, a closure can use variables from the code around it. It
**captures** them:

```rust
let threshold = 10;
let is_big = |x: i32| x > threshold;   // uses threshold from outside
is_big(11)                             // true
```

A `fn` written in the same place could not see `threshold`.

## How closures capture: Fn, FnMut and FnOnce

A closure captures each outside variable in the gentlest way its body
allows, and that decides how it can be called. Rust names the three kinds
with three traits:

| The body... | Captures by | Trait | Can be called |
|---|---|---|---|
| only reads the variable | `&` shared reference | `Fn` | any number of times |
| changes it | `&mut` reference | `FnMut` | many times, but needs `mut` |
| moves it away (drops it, returns it) | value (ownership) | `FnOnce` | once only |

```rust
let name = String::from("Ana");
let greet = || format!("hi {name}");     // reads name: Fn

let mut count = 0;
let mut tick = || count += 1;            // changes count: FnMut, so `let mut tick`
tick();
tick();                                  // count is now 2

let consume = || drop(name);             // moves name away: FnOnce
consume();
// consume();     // uncomment: error[E0382] use of moved value: `consume`
```

(A fragment; `drop` takes a value and drops it on the spot.) These are the
ownership and borrowing rules of lessons 4 and 5, applied to closures: while
`tick` holds `&mut count`, nothing else may use `count`.

A function that takes a closure says which kind it accepts, as a trait bound
(lesson 10):

```rust
fn twice<F: Fn(i32) -> i32>(f: F, x: i32) -> i32 {
    f(f(x))
}
twice(|n| n + 3, 1);    // 7: (1 + 3) + 3
```

`F: Fn(i32) -> i32` reads "`F` is any closure (or function) that takes an
`i32`, returns an `i32`, and can be called repeatedly". Asking for `FnMut`
instead would also accept closures that change state, and `FnOnce` would
accept every closure but allow only one call.

### move, and returning closures

A function can return a closure, written with `impl Fn(...)` as the return
type. The first attempt does not compile:

```rust
fn make_adder(n: i32) -> impl Fn(i32) -> i32 {
    |x| x + n
}
```

```text
error[E0373]: closure may outlive the current function, but it borrows `n`, which is owned by the current function
 --> src/lib.rs:2:5
  |
2 |     |x| x + n
  |     ^^^     - `n` is borrowed here
  |     |
  |     may outlive borrowed value `n`
  |
help: to force the closure to take ownership of `n` (and any other referenced variables), use the `move` keyword
  |
2 |     move |x| x + n
  |     ++++
```

The closure only reads `n`, so it borrows it. But `n` is a parameter of
`make_adder`, dropped when `make_adder` returns, and the closure lives on
after that: it would hold a reference to nothing (lesson 5's dangling
reference). `move` in front of the closure makes it take its captured
variables **by value**, so it carries its own copy of `n`:

```rust
fn make_adder(n: i32) -> impl Fn(i32) -> i32 {
    move |x| x + n
}
let add5 = make_adder(5);
add5(10)       // 15
```

`move` decides *how* variables are captured, not what the closure does with
them; this one still only reads `n`, so it is still `Fn`. You also need
`move` when handing a closure to a new thread (Advanced track).

## Iterators

An **iterator** is anything that produces a sequence of values, one at a
time, on request. It is defined by the `Iterator` trait, which has a single
required method:

```rust
trait Iterator {
    type Item;                                // the type of value it produces
    fn next(&mut self) -> Option<Self::Item>; // the next value, or None when done
}
```

(How the standard library defines it, shortened.) Each call to `next` gives
`Some(value)`, until the sequence is over and it gives `None`. Every other
iterator method (`map`, `filter`, `sum`, more than seventy of them) is a
default method built on `next`, the pattern of lesson 10.

A `for` loop is itself written on top of this. `for x in v { ... }` turns `v`
into an iterator and is roughly:

```rust
let mut iter = v.into_iter();
while let Some(x) = iter.next() {
    // loop body
}
```

`while let` is `if let` (lesson 7) in a loop: keep going as long as the
pattern fits.

Collections give you iterators in three flavours, which differ in ownership:

```rust
let v = vec![1, 2, 3];
v.iter()          // produces &i32: borrows v, v is still usable afterwards
v.iter_mut()      // produces &mut i32: borrows v mutably, to change items
v.into_iter()     // produces i32: consumes v, which is gone afterwards
```

Others: `"a b".split_whitespace()` produces `&str`, `s.chars()` produces
`char`, and a range like `1..=5` is an iterator itself.

## Adapters, consumers, and laziness

Iterator methods come in two groups:

- **Adapters** take an iterator and return a new iterator that changes the
  values on the way: `map` (transform each one), `filter` (keep some),
  `enumerate` (pair each with its position), `zip` (pair with another
  iterator), `rev`, `skip`, `take`, `chain`, `flat_map`, `scan`.
- **Consumers** pull every value through and produce a final result:
  `collect`, `sum`, `count`, `min`, `max`, `fold`, `any`, `all`, `find`,
  `position`, `for_each`.

Adapters are **lazy**: they do nothing on their own. They only describe the
work, and the work happens when a consumer pulls the values through. A
chain without a consumer computes nothing, and the compiler warns about it:

```rust
v.iter().map(|n| n * 2);
```

```text
warning: unused `Map` that must be used
  |
3 |     v.iter().map(|n| n * 2);
  |     ^^^^^^^^^^^^^^^^^^^^^^^
  |
  = note: iterators are lazy and do nothing unless consumed
```

Here is how values move through the chain from the start of the lesson.
`collect` asks for one value at a time, and each request travels up the
chain:

| `1..=5` gives | `filter` (odd?) | `map` (square) | `collect` has |
|---|---|---|---|
| 1 | keep | 1 | `[1]` |
| 2 | drop | | `[1]` |
| 3 | keep | 9 | `[1, 9]` |
| 4 | drop | | `[1, 9]` |
| 5 | keep | 25 | `[1, 9, 25]` |
| `None` | | | done |

Each value goes all the way through before the next starts; no in-between
vector is built.

`collect` can build many kinds of collection, so it must be told which:
annotate the variable (`let squares: Vec<i32> = ...`) or name it on the call,
`.collect::<Vec<_>>()`. It can also build a `String` from `char`s, a
`HashMap` from pairs, or a `HashSet`.

## References in closures

`v.iter()` produces `&i32`. `filter` then hands its closure a reference to
each item, so it can look without taking it, which makes the closure's
parameter a `&&i32`, a reference to a reference. Compare it with a number
directly and the compiler says so:

```rust
v.iter().filter(|n| n > 1)
```

```text
error[E0308]: mismatched types
  |
2 |     v.iter().filter(|n| n > 1).count()
  |                             ^ expected `&&i32`, found integer
```

Three ways to peel the references off:

```rust
v.iter().filter(|&&n| n > 1)           // a pattern: &&n matches the two & and binds n: i32
v.iter().filter(|n| **n > 1)           // dereference twice
v.iter().copied().filter(|n| *n > 1)   // copied() turns each &i32 into an i32 first
```

(Each a fragment.) `map` gives its closure the item itself, not a reference
to it, so after `v.iter()`, `map(|n| n * 2)` sees one `&i32`, and arithmetic
works on that directly. When in doubt, write the simple version and let the
`expected ..., found ...` message tell you how many `&` there are.

## fold

`fold` is the general consumer: it carries a running value, the
**accumulator**, through the sequence. You give it a starting value and a
closure that combines the accumulator with each item:

```rust
let product = (1..=5).fold(1, |acc, n| acc * n);   // 120
```

| `n` | `acc` before | `acc * n` |
|---|---|---|
| 1 | 1 | 1 |
| 2 | 1 | 2 |
| 3 | 2 | 6 |
| 4 | 6 | 24 |
| 5 | 24 | 120 |

`sum`, `count` and `max` are all special cases of `fold`. `scan` is its
adapter cousin: it carries an accumulator too, but produces each intermediate
value as it goes, instead of only the final one.

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

    let mut count = 0;
    let mut tick = || count += 1;
    tick();
    tick();
    println!("{count}");

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
2
[1, 9, 25]
[2, 3] [2, 3]
120
7 15
[10, 20] [1, 2]
```

`a` holds `&i32` values (references into `v`) and `b` holds copies; both
print the same. `make_adder(10)(5)` makes an adder and calls it at once. The
last line is laziness made visible: `take(2)` asked for two values, so the
closure ran twice and never saw `3`.

## Your turn

In `src/lib.rs`, preferably with iterator chains rather than `for` loops:

- `evens_squared(nums)`: the squares of the even numbers, in their original
  order: `[1, 2, 3, 4, -6]` gives `[4, 16, 36]` (negative even numbers count)
- `count_long_words(text, min_len)`: how many whitespace-separated words have
  **at least** `min_len` bytes (`.len()`): in `"a quick brown fox jumps"`,
  three words have 5 or more
- `running_totals(nums)`: each item is the sum of everything up to and
  including that position: `[1, 2, 3, 4]` becomes `[1, 3, 6, 10]`; an empty
  slice gives an empty vector
- `make_adder(n)`: returns a closure that adds `n` to its argument (the
  starter already has the `move`)
- `apply_n(f, times, x)`: calls `f` on `x`, then on the result, `times` times
  in all: `apply_n(|x| x * 2, 10, 1)` is 1024, and `times` 0 gives `x`
  unchanged
