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

Ownership is the idea that makes Rust different from every language you may
have used before, so this lesson starts with the problem it solves.

## Background: where values live

A running program keeps its data in two places:

- The **stack** holds values whose size is known when the program is
  compiled: an `i32`, a `bool`, a fixed-size tuple. Each function call puts
  its local variables on top of the stack, and they are removed, all at once,
  when the function returns. That is fast and automatic, like a stack of
  plates: you only ever add to or take from the top.
- The **heap** holds values whose size is only known while the program runs,
  or can change: the text of a `String`, the items of a `Vec`. The program
  asks for a block of heap memory of the size it needs, gets back its
  address, and must give the block back when it is done.

That last step, giving heap memory back, is where languages differ. Python,
Java and JavaScript run a **garbage collector**, which finds and frees
memory nobody uses any more, at the cost of extra work while the program
runs. C makes you free memory by hand, and freeing too early, too late or
twice is the source of a large share of all security bugs. Rust does
neither. It follows a set of rules, checked by the compiler, that decide
exactly when each value is freed.

## The rules

1. Each value has an **owner**: the variable, or the struct field, vector
   slot and so on, that it belongs to.
2. There is only one owner at a time.
3. When the owner goes out of scope, the value is **dropped**: its memory is
   freed, automatically.

A variable's **scope** is the block, between `{` and `}`, where it was
declared. When the block ends, its variables are dropped, in reverse order.
Ownership can be handed on to another owner, which is called a **move**, and
after a move the old owner can no longer be used.

## Moves

A `String` is three numbers on the stack (an address, a length and a
capacity) plus the text itself on the heap:

```text
 stack                     heap
 a: [ addr | len 5 | cap 5 ] ----> h e l l o
```

What should `let b = a;` do? Copying only the stack part would give two
owners of one heap block, and when both were dropped the block would be
freed twice, a **double free**, which corrupts memory. Copying the heap text
too would be slow and invisible. Rust does a third thing: it copies the
stack part and makes `a` unusable, so `b` is the only owner:

```text
 stack                     heap
 a: (moved, unusable)
 b: [ addr | len 5 | cap 5 ] ----> h e l l o
```

In code:

```rust
let a = String::from("hello");
let b = a;              // the String moves from a to b
println!("{a}");        // error[E0382]: borrow of moved value: `a`
```

Here is the full message. Read it the way the Hello lesson described:

```text
error[E0382]: borrow of moved value: `a`
 --> src/lib.rs:4:16
  |
2 |     let a = String::from("hello");
  |         - move occurs because `a` has type `String`, which does not implement the `Copy` trait
3 |     let b = a;
  |             - value moved here
4 |     println!("{a}");
  |                ^ value borrowed here after move
  |
help: consider cloning the value if the performance cost is acceptable
  |
3 |     let b = a.clone();
  |              ++++++++
```

The three labelled lines tell the whole story in order: `a` is a `String`,
which is not `Copy` (see below), so line 3 moved it, so line 4 cannot use
it. The `help:` offers one fix, `clone`, and its wording, "if the
performance cost is acceptable", is a hint that it is not always the right
one; often the better fix is to borrow (next lesson). `rustc --explain E0382`
explains this error at length.

Passing a value to a function moves it too: the parameter becomes the new
owner, and the value is dropped when the function ends.

```rust
fn consume(s: String) { }

let name = String::from("Ana");
consume(name);
// consume(name);       // uncomment: error[E0382], name was moved by the first call
```

A function can give ownership back by returning the value, which moves it
out to the caller.

## clone

When you really want two independent copies, say so:

```rust
let a = String::from("hello");
let b = a.clone();      // deep copy: both a and b are usable
```

`clone` copies the heap data as well, so now there are two separate
strings, each with its own owner. It is explicit because it can be
expensive, and Rust wants you to see where copies happen. A useful
consequence: any copy Rust makes *without* being asked is always cheap.

## Copy types

Small values that live entirely on the stack (integers, floats, `bool`,
`char`, and tuples or arrays of those) are **copied** instead of moved:

```rust
let x = 5;
let y = x;
println!("{x} {y}");    // fine: i32 is Copy
```

This looks exactly like the `String` example, and behaves differently. An
`i32` owns no heap memory, so copying its bits is both cheap and safe: there
is nothing to free twice. Types like that implement the `Copy` trait (traits
are lesson 10), which is what the "does not implement the `Copy` trait" in
the error above refers to. A type that owns heap memory, such as `String` or
`Vec`, can never be `Copy`.

## Moving out of a collection

You cannot move one item out of a `Vec` by index, because that would leave a
hole the vector still owns, and the vector would later try to drop it:

```rust
let names = vec![String::from("Ana")];
let first = names[0];           // error[E0507]: cannot move out of index
let first = names[0].clone();   // fine
let first = &names[0];          // also fine: borrow it (next lesson)
```

(Three alternatives.) The compiler offers both fixes itself:

```text
error[E0507]: cannot move out of index of `Vec<String>`
  |
3 |     let first = names[0];
  |                 ^^^^^^^^ move occurs because value has type `String`, which does not implement the `Copy` trait
  |
help: consider borrowing here
  |
3 |     let first = &names[0];
  |                 +
help: consider cloning the value if the performance cost is acceptable
  |
3 |     let first = names[0].clone();
  |                         ++++++++
```

## Loops move too

`for item in vec` consumes the vector: each item is moved out of it into
`item`, and afterwards the vector is gone:

```rust
for w in words { }
words.len();            // error: borrow of moved value
for w in &words { }     // loops over references, words survives
```

(Three lines from inside a function.) `&words` lends the vector to the loop
instead, so `w` is a reference to each item and `words` is still there
afterwards. The `&` is borrowing, the next lesson.

## Mutability belongs to the binding

```rust
fn exclaim(s: String) -> String {
    s.push('!');        // error[E0596]: cannot borrow `s` as mutable
    s
}
```

```text
error[E0596]: cannot borrow `s` as mutable, as it is not declared as mutable
  |
2 |     s.push('!');
  |     ^ cannot borrow as mutable
  |
help: consider changing this to be mutable
  |
1 | pub fn exclaim(mut s: String) -> String {
  |                +++
```

Ownership of `s` came with the call, but the binding (the name) is
immutable, like any `let` without `mut`. Write `mut s` in the parameter
list. That does not change the function's signature: callers still pass a
`String` and get a `String` back, and they cannot tell the difference. The
`mut` only says that the function may change its own copy.

## The working versions, run

```rust
fn consume(s: String) -> usize {
    s.len()
}

fn main() {
    let a = String::from("hello");
    let b = a.clone();          // two independent Strings
    println!("{a} {b}");

    let x = 5;
    let y = x;                  // i32 is Copy
    println!("{x} {y}");

    let names = vec![String::from("Ana")];
    let first = &names[0];      // borrow, do not move
    println!("{first} {}", names.len());

    let n = consume(b);         // b moves in; using b after this would not compile
    println!("{n}");

    let words = vec!["a", "b"];
    for w in &words {
        print!("{w} ");
    }
    println!("{}", words.len()); // still here: the loop borrowed it
}
```

```output
hello hello
5 5
Ana 1
5
a b 2
```

Each line that compiles here is the fix for one of the errors above. Try
breaking it on purpose: add `println!("{b}");` after the `consume(b)` line
and read the error.

## Your turn

Make `cargo check` succeed, and make the functions do what their comments
say, without changing any function signatures: the parameter and return
types stay as they are (adding `mut` before a parameter's name is fine, as
explained above). Fix the errors one at a time, from the top, and re-run
`cargo check` after each fix: one fix often clears several messages, or
reveals the next. Then press **Check**.
