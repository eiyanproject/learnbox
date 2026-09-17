---
title: Ownership
summary: Moves, clones and copies. This starter does not compile; fixing it is the lesson.
order: 4
files: [src/lib.rs]
run: cargo check
hints:
  - "Read each error from the top. `cannot borrow as mutable` on `exclaim`: the parameter needs `mut`, as in `fn exclaim(mut s: String)`."
  - "`cannot move out of index`: you cannot take a `String` out of a `Vec` by position and leave a hole. Take a copy with `names[0].clone()`."
  - "`use of moved value` in `twice`: after `let a = s;`, `s` is gone. Clone before moving: `let a = s.clone();`."
  - "In `shout_all`, `for w in words` moves the vector into the loop. Loop over a borrow instead, `for w in &words`, so `words.len()` still works afterwards."
---

**This lesson's starter code does not compile.** Run `cargo check`, read
the errors, and fix them one by one. You will spend a lot of time with these
four errors in your first weeks of Rust; after this, they will look familiar.

## The rules

Rust manages memory without a garbage collector by following three rules:

1. Every value has exactly one **owner**, a variable.
2. When the owner goes out of scope, the value is **dropped** (freed).
3. Ownership can be **moved** to another variable, and then the old one can no
   longer be used.

## Moves

```rust
let a = String::from("hello");
let b = a;              // the String moves from a to b
println!("{a}");        // error[E0382]: borrow of moved value: `a`
```

A `String` owns heap memory. If `let b = a;` copied just the pointer, both
would free the same memory when dropped. Rust avoids that by declaring `a`
invalid instead.

Passing a value to a function moves it too:

```rust
fn consume(s: String) { }

let name = String::from("Ana");
consume(name);
consume(name);          // error: value used after move
```

A function can give ownership back by returning the value.

## clone

When you really want two independent copies, say so:

```rust
let a = String::from("hello");
let b = a.clone();      // deep copy: both a and b are usable
```

`clone` is explicit because it can be expensive, and Rust wants you to see
where copies happen.

## Copy types

Small values that live entirely on the stack (integers, floats, `bool`,
`char`, and tuples or arrays of those) are **copied** instead of moved:

```rust
let x = 5;
let y = x;
println!("{x} {y}");    // fine: i32 is Copy
```

## Moving out of a collection

You cannot move one item out of a `Vec` by index, because that would leave a
hole the vector still owns:

```rust
let names = vec![String::from("Ana")];
let first = names[0];           // error[E0507]: cannot move out of index
let first = names[0].clone();   // fine
let first = &names[0];          // also fine: borrow it (next lesson)
```

## Loops move too

`for item in vec` consumes the vector. Afterwards the vector is gone:

```rust
for w in words { }
words.len();            // error: borrow of moved value
for w in &words { }     // loops over references, words survives
```

## Mutability belongs to the binding

```rust
fn exclaim(s: String) -> String {
    s.push('!');        // error[E0596]: cannot borrow `s` as mutable
    s
}
```

Ownership of `s` came with the call, but the binding is immutable. Write
`mut s` in the parameter list.

## Your turn

Make `cargo check` succeed without changing any function signatures, and
make the functions do what their comments say. Then press **Check**.
