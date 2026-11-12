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

The ownership rules of the Beginner track are: every value has exactly one
owner, and you may have many shared references or one mutable reference, all
checked at compile time. Those rules handle most programs. This lesson is
about three situations they cannot express, and the standard library type
that solves each:

| Problem | Type | What it does |
|---|---|---|
| a type that contains itself (a tree, a list) | `Box<T>` | puts a value on the heap, with one owner |
| one value that genuinely has several owners | `Rc<T>` | counts owners; drops the value when the last one goes |
| changing a value that is only reachable through shared references | `RefCell<T>` | checks the borrow rules at run time instead |

All three are **smart pointers**: structs that own some data, point to it,
and add behaviour on top (freeing, counting, checking). `String` and `Vec`
are smart pointers already: each owns a heap buffer and frees it when
dropped. A smart pointer acts like a reference to what it holds, so
`boxed.len()` or `*boxed` work as on the value itself; that comes from the
`Deref` trait, which these types implement.

## Box<T>: a value on the heap

`Box::new(x)` moves `x` to the heap and gives back a `Box`, a pointer that
**owns** it. When the box is dropped, the value inside is dropped and its
heap memory freed, exactly like any owned value. A `Box` adds no other
cost: it is one pointer in size, with no counter and no checks.

Why put a value on the heap at all? The main reason is **recursive types**.
Try a linked list, where each cell holds a number and the rest of the list:

```rust
pub enum List {
    Cons(i32, List),
    Nil,
}
```

```text
error[E0072]: recursive type `List` has infinite size
 --> src/lib.rs:1:1
  |
1 | pub enum List {
  | ^^^^^^^^^^^^^
2 |     Cons(i32, List),
  |               ---- recursive without indirection
  |
help: insert some indirection (e.g., a `Box`, `Rc`, or `&`) to break the cycle
  |
2 |     Cons(i32, Box<List>),
  |               ++++    +
```

The compiler must know the size of every type. To size a `List`, it needs
the size of a `Cons`, which contains a `List`, which contains a `Cons`, and
so on forever. A `Box<List>` is always one pointer, whatever it points to,
so the size becomes "an `i32` plus a pointer". The rest of the list lives
on the heap, one box after another:

```text
 list: Cons(1, ●)
               └──> heap: Cons(2, ●)
                                  └──> heap: Nil
```

That is what the `help:` calls **indirection**: holding a pointer to the
value instead of the value itself.

Box's other uses you have already met: `Box<dyn Trait>`, a value whose
concrete type is only known at run time (Beginner lesson 10), and
`Box<dyn Error>` (lesson 2).

## Rc<T>: shared ownership

Sometimes a value genuinely has several owners, and none of them is in
charge of when it ends: a node in a graph that several edges point to, or a
configuration that many parts of a program hold on to. With one owner, you
would have to pick one part to own it and prove the others never outlive
it, which may not be possible.

`Rc<T>` (**r**eference **c**ounted) allows several owners. It keeps the value
on the heap next to a counter of how many `Rc` handles exist:

```rust
use std::rc::Rc;

let shared = Rc::new(String::from("config"));
let a = Rc::clone(&shared);      // cheap: adds 1 to the counter, no deep copy
let b = Rc::clone(&shared);
Rc::strong_count(&shared)        // 3
```

(A fragment.) `shared`, `a` and `b` are three handles to the **same**
`String`:

```text
 shared ─┐
 a ──────┼──> heap: [ count: 3 | "config" ]
 b ──────┘
```

Each handle dropped lowers the count, and when the last one goes, the count
reaches 0 and the `String` is dropped. The ownership rules still hold; the
value's single "owner" is now the group of handles together.

`Rc::clone(&shared)` is written that way, rather than `shared.clone()`, by
convention: both do the same thing, but `Rc::clone` makes it visible that
this is a cheap count increment, not a deep copy like `String::clone`.

`Rc` gives only **shared** access, like `&T`. With several owners, letting
any one of them change the value would break "one writer or many readers":

```rust
let shared = Rc::new(vec![1]);
shared.push(2);
```

```text
error[E0596]: cannot borrow data in an `Rc` as mutable
  |
4 |     shared.push(2);
  |     ^^^^^^ cannot borrow as mutable
  |
  = help: trait `DerefMut` is required to modify through a dereference, but it is not implemented for `Rc<Vec<i32>>`
```

`Rc` is for one thread only; its counter is not safe to change from two
threads at once, and the compiler stops you from sending it to another
thread. `Arc` is the thread-safe version (Advanced track).

## RefCell<T>: the borrow rules, checked at run time

Sometimes you need to change a value that you can only reach through a
shared reference, such as the contents of an `Rc`. `RefCell<T>` makes this
possible by moving the borrow check from compile time to run time. You ask
it for a borrow, and it keeps count:

```rust
use std::cell::RefCell;

let log = RefCell::new(Vec::new());
log.borrow_mut().push("started");      // exclusive borrow, while this line runs
println!("{:?}", log.borrow());         // shared borrow
```

(A fragment.) Note that `log` is not `mut`, and yet its contents changed:
`borrow_mut` works through `&self`. This is called **interior mutability**:
the mutation happens inside a value that looks immutable from outside.

- `borrow()` returns a `Ref<T>`, which acts like `&T`;
- `borrow_mut()` returns a `RefMut<T>`, which acts like `&mut T`;
- the borrow lasts until that `Ref` or `RefMut` is dropped. A temporary, as
  in the two lines above, is dropped at the end of its statement.

The rule is the same as at compile time: many `Ref`s, or one `RefMut`, never
both. The difference is what happens when you break it. Instead of a
compile error, you get a **panic** when the program runs:

```rust
fn main() {
    let log = RefCell::new(vec![1]);
    let reading = log.borrow();
    log.borrow_mut().push(2);         // panics: `reading` is still alive
    println!("{}", reading.len());
}
```

```text
thread 'main' (4242) panicked at src/main.rs:4:9:
RefCell already borrowed
```

(Older Rust versions word it as `already borrowed: BorrowMutError`.) This is
the price of `RefCell`: a mistake the compiler would have caught now
surfaces only when that code runs. When panicking is not acceptable,
`try_borrow()` and `try_borrow_mut()` return a `Result` instead: `Err` when
the borrow is not possible right now.

`RefCell` is also one-thread only; `Mutex` and `RwLock` are the thread-safe
equivalents (Advanced track).

## Rc<RefCell<T>>: shared and mutable

Put the two together, and you get several owners that can all change the
same value: `Rc` provides the sharing, `RefCell` the mutation:

```rust
let counter = Rc::new(RefCell::new(0));
let other = Rc::clone(&counter);
*other.borrow_mut() += 1;
assert_eq!(*counter.borrow(), 1);
```

(A fragment.) Reading the third line from the inside out: `other` is an
`Rc`, which acts as a reference to the `RefCell`; `.borrow_mut()` asks the
`RefCell` for exclusive access and gets a `RefMut<i32>`; `*` reaches the
`i32` inside it; `+= 1` changes it. The change is visible through `counter`,
because both handles point at the same `RefCell`.

This combination is the standard tool for shared, mutable state in
single-threaded code, and its counterpart with threads is `Arc<Mutex<T>>`.
Reach for it only when ownership really is shared: it trades compile-time
guarantees for run-time checks. And note one trap: if two `Rc`s point at
each other, neither count ever reaches 0, and both values leak. The
Advanced track shows `Weak`, a non-owning `Rc`, for such back-references.

## Run it

```rust
use std::cell::RefCell;
use std::rc::Rc;

enum List {
    Cons(i32, Box<List>),
    Nil,
}

fn sum(list: &List) -> i32 {
    match list {
        List::Cons(v, rest) => v + sum(rest),
        List::Nil => 0,
    }
}

fn main() {
    let list = List::Cons(1, Box::new(List::Cons(2, Box::new(List::Nil))));
    println!("{}", sum(&list));

    let shared = Rc::new(String::from("config"));
    let a = Rc::clone(&shared);
    {
        let _b = Rc::clone(&shared);
        println!("{}", Rc::strong_count(&shared));
    }                                   // _b dropped: the count goes down
    println!("{} {}", Rc::strong_count(&shared), a);

    let log = RefCell::new(Vec::new());
    log.borrow_mut().push("started");
    println!("{:?}", log.borrow());
    let held = log.borrow();
    println!("{}", log.try_borrow_mut().is_err());   // a shared borrow is alive
    drop(held);
    println!("{}", log.try_borrow_mut().is_ok());

    let counter = Rc::new(RefCell::new(0));
    let other = Rc::clone(&counter);
    *other.borrow_mut() += 1;
    println!("{}", counter.borrow());
}
```

```output
3
3
2 config
["started"]
true
true
1
```

Line by line: `sum` follows the boxes, 1 + 2 + 0. Three handles while `_b`
existed, two after its block ended, and `a` still reads the same `String`.
`held` is a live `Ref`, so `try_borrow_mut` failed, without panicking;
`drop(held)` ended that borrow early, and the next try succeeded. Finally the
`+= 1` through `other` was seen through `counter`. (`sum(rest)` works because
`rest` is a `&Box<List>`, and the `Box` acts as a reference to the `List`
inside it.)

## Your turn

In `src/lib.rs`:

- `Expr`, a recursive enum with `Num(f64)`, `Add`, `Mul` (two boxed
  sub-expressions each) and `Neg` (one boxed sub-expression)
- `eval()`: the value of the expression. The tests build an expression 1000
  levels deep, so recursion must work for that (plain recursion does).
- `Display`, fully parenthesised: every `Add` and `Mul` in brackets, with
  spaces around the operator, `Neg` as a `-` directly in front, and numbers
  printed with `{}`, which shows `1.0` as `1` and `0.5` as `0.5`.
  `mul(add(num(1.0), num(2.0)), neg(num(3.0)))` prints `((1 + 2) * -3)`.
- the helpers `add`, `mul` and `neg` (`num` is given), each taking plain
  `Expr` values and boxing them
- `SharedLog`, several handles to one list of entries, stored as
  `Rc<RefCell<Vec<String>>>`:
  - `new()`, an empty log with one handle
  - `clone_handle()`, a new handle to the **same** entries
  - `push(&self, entry: &str)`: takes `&self`, not `&mut self`, so the
    `RefCell` is what makes the change possible
  - `entries()`, a copy of the entries as a `Vec<String>`
  - `handle_count()`, how many handles exist right now
  - `try_push(&self, entry: &str) -> bool`: adds the entry and returns
    `true`, or, when the entries are currently borrowed (the provided
    `with_entries` holds a borrow while its closure runs), changes nothing
    and returns `false` instead of panicking
