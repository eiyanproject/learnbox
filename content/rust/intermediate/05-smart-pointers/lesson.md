---
title: Smart pointers
summary: Box for recursive types and heap values, Rc for shared ownership, RefCell for checked mutation behind a shared reference.
order: 5
files: [src/lib.rs]
run: cargo test
hints:
  - "`Expr` is `enum Expr { Num(f64), Add(Box<Expr>, Box<Expr>), Mul(Box<Expr>, Box<Expr>), Neg(Box<Expr>) }`, and `eval` recurses with `match self`."
  - "The helpers wrap in a box: `pub fn add(a: Expr, b: Expr) -> Expr { Expr::Add(Box::new(a), Box::new(b)) }`."
  - "`SharedLog` holds `Rc<RefCell<Vec<String>>>`; `clone_handle` is `SharedLog { entries: Rc::clone(&self.entries) }`, and `push` uses `self.entries.borrow_mut().push(...)`."
  - "`handle_count` is `Rc::strong_count(&self.entries)`. `try_push` uses `self.entries.try_borrow_mut()` and returns `false` when that fails."
---

A **smart pointer** is a struct that owns data and acts like a reference to it.
`String` and `Vec` are smart pointers already. Three more solve problems plain
ownership cannot.

## Box<T>: a value on the heap

`Box::new(x)` moves `x` to the heap and gives you a single owner pointing at it.
Its main uses:

- **Recursive types.** A type cannot contain itself directly (its size would be
  infinite), but it can contain a `Box` of itself, which has a fixed size:

```rust
enum List {
    Cons(i32, Box<List>),
    Nil,
}
```

- **Trait objects**: `Box<dyn Shape>` (you used this in Beginner: Traits).
- Moving a large value around without copying it.

## Rc<T>: shared ownership

Sometimes one value genuinely has several owners, such as a node in a graph or a
configuration shared by many components. `Rc` (reference counted) allows that:

```rust
use std::rc::Rc;

let shared = Rc::new(String::from("config"));
let a = Rc::clone(&shared);      // cheap: increments a counter, no deep copy
let b = Rc::clone(&shared);
Rc::strong_count(&shared)        // 3
```

The value is dropped when the last `Rc` goes away. `Rc` gives only **shared**
(`&`) access. It is single-threaded; `Arc` is the thread-safe version (Advanced track).

## RefCell<T>: mutation checked at runtime

The borrow rules (many `&` or one `&mut`) are normally checked at compile time.
`RefCell` moves the check to runtime, so you can mutate through a shared reference:

```rust
use std::cell::RefCell;

let log = RefCell::new(Vec::new());
log.borrow_mut().push("started");      // RefMut: exclusive, at runtime
println!("{:?}", log.borrow());         // Ref: shared
```

Break the rule (a `borrow_mut` while another borrow is alive) and it **panics**.
`try_borrow_mut` returns a `Result` instead.

## Rc<RefCell<T>>: shared and mutable

The combination is the standard way to have several owners that can all change
the same value:

```rust
let counter = Rc::new(RefCell::new(0));
let other = Rc::clone(&counter);
*other.borrow_mut() += 1;
assert_eq!(*counter.borrow(), 1);
```

Reach for it only when ownership really is shared. It trades compile-time
guarantees for runtime checks, and `Rc` cycles leak (the Advanced track shows
`Weak` for back-references).

## Your turn

In `src/lib.rs`:

- `Expr`: a recursive enum with `Num(f64)`, `Add`, `Mul` and `Neg` using `Box`;
  `eval()` computes the value; `to_string()` via `Display` prints fully
  parenthesised: `((1 + 2) * -3)`
- helpers `num`, `add`, `mul`, `neg` that build boxed nodes
- `SharedLog`: several handles to one list of entries (`Rc<RefCell<Vec<String>>>`):
  `new`, `clone_handle`, `push(&self, entry)` (note: `&self`), `entries()` (a copy),
  `handle_count()`, and `try_push` returning `false` instead of panicking when the log
  is already borrowed
