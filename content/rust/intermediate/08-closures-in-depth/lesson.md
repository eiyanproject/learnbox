---
title: Closures in depth
summary: Fn, FnMut and FnOnce, how captures work, move closures, storing closures in structs, and returning them.
order: 8
files: [src/lib.rs]
run: cargo test
hints:
  - "`EventBus` stores `handlers: HashMap<String, Vec<Box<dyn Fn(&str) -> String>>>`. `on` takes `impl Fn(&str) -> String + 'static` and pushes `Box::new(handler)`."
  - "`make_counter()` returns `impl FnMut() -> u32`: `let mut count = 0; move || { count += 1; count }`."
  - "`apply_twice<F: FnMut(i32) -> i32>(mut f: F, x: i32) -> i32 { let y = f(x); f(y) }`; the parameter must be `mut` because calling an `FnMut` changes it."
  - "`run_once<F: FnOnce() -> String>(f: F) -> String { f() }`. `compose` returns `impl Fn(i32) -> i32` with `move |x| g(f(x))`, requiring `F: Fn(i32) -> i32` and `G: Fn(i32) -> i32`."
---

The Beginner track passed closures to iterator adapters. This lesson looks at
what a closure actually is, which decides where you can use it.

## What a closure captures

A closure captures variables from its surroundings in the least demanding way
that works:

```rust
let name = String::from("Ana");
let greet = || println!("hi {name}");     // borrows name immutably

let mut count = 0;
let mut inc = || count += 1;              // borrows count mutably

let data = vec![1, 2, 3];
let consume = move || drop(data);         // takes ownership of data
```

## The three traits

Every closure implements one or more of these, depending on what it does with
its captures:

| Trait | Can be called | The closure... |
|---|---|---|
| `Fn` | many times, through `&self` | only reads captures |
| `FnMut` | many times, through `&mut self` | changes captures |
| `FnOnce` | once, consuming `self` | moves a capture out |

Every `Fn` is also `FnMut`, and every `FnMut` is also `FnOnce`. So when
**accepting** a closure, ask for the least you need: `FnOnce` accepts the most
closures, `Fn` the fewest.

```rust
fn call_n<F: FnMut()>(mut f: F, n: usize) {
    for _ in 0..n { f(); }
}
```

## move

`move` makes the closure take ownership of everything it captures. You need it
whenever the closure outlives the current scope: returning it, storing it, or
sending it to a thread. `move` affects **how** things are captured, not which
trait the closure implements: a `move` closure that only reads is still `Fn`.

## Returning closures

Each closure has its own unnamed type, so you return it as `impl Fn...`:

```rust
fn adder(n: i32) -> impl Fn(i32) -> i32 {
    move |x| x + n
}
```

## Storing closures

A struct or collection holding **different** closures needs trait objects, because
each closure is a different type:

```rust
struct Button {
    on_click: Vec<Box<dyn Fn() -> String>>,
}
```

`Box<dyn Fn>` stored in a struct needs its captures to live long enough; for a
struct that owns its callbacks, the bound is `'static`, which `move` closures
over owned data satisfy.

A struct holding **one** closure can instead be generic, `struct Retry<F: Fn()> { f: F }`,
which avoids the box and the dynamic call.

## Your turn

In `src/lib.rs`:

- `EventBus`: `on(event, handler)` registers a `Fn(&str) -> String` handler;
  `emit(event, payload)` calls every handler for that event in registration order
  and returns their outputs; `handler_count(event)`
- `make_counter()`: returns a closure that returns 1, 2, 3, ... on successive calls
- `apply_twice(f, x)`: accepts `FnMut`
- `run_once(f)`: accepts `FnOnce`, so a closure that moves a `String` out works
- `compose(f, g)`: returns a closure computing `g(f(x))`
