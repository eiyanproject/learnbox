---
title: Generics and lifetimes
summary: Write one type or function for many types, and tell the compiler how long borrowed data lives.
order: 12
files: [src/lib.rs]
run: cargo test
hints:
  - "`longest<'a>(a: &'a str, b: &'a str) -> &'a str`: `if b.len() > a.len() { b } else { a }`. The shared `'a` is the whole trick."
  - "`Stack<T>` wraps a `Vec<T>`: `new` is `Stack { items: Vec::new() }`, `push` calls `self.items.push(item)`, `pop` returns `self.items.pop()`."
  - "`peek(&self) -> Option<&T>` is `self.items.last()`."
  - "`Excerpt::first_sentence(&self) -> &'a str`: find the first `'.'` with `self.text.find('.')` and slice up to and including it; if there is none, return the whole text."
---

This lesson has two parts that look alike on the page, because both are
written in `<...>` after a name, but answer different questions:

- **Generics** answer "which *type*?": write a struct or function once, with
  a placeholder for a type, and use it with many types.
- **Lifetimes** answer "borrowed from *where*, and for how long?": when a
  function returns a reference, or a struct holds one, say which input it
  borrows from, so the compiler can check it never outlives that input.

## Generics

Without generics, a pair of numbers and a pair of strings would need two
nearly identical structs, `PairI32` and `PairStr`, and every bug fixed twice.
A **type parameter**, conventionally `T`, stands in for "some type, chosen by
whoever uses this":

```rust
struct Pair<T> {
    first: T,
    second: T,
}

impl<T> Pair<T> {
    fn new(first: T, second: T) -> Self {
        Self { first, second }
    }

    fn swap(self) -> Self {
        Self { first: self.second, second: self.first }
    }
}

let p = Pair::new(1, 2);          // Pair<i32>
let q = Pair::new("a", "b");      // Pair<&str>
```

(A fragment.) Reading the declarations:

- `struct Pair<T>`: "`Pair` has a type parameter `T`"; both fields have that
  type, so a `Pair` holds two values *of the same type*.
- `impl<T> Pair<T>`: the first `<T>` declares the parameter for this block,
  the second uses it. Read it as "for any type `T`, here are the methods of
  `Pair<T>`".
- At `Pair::new(1, 2)`, the compiler works out that `T` is `i32` from the
  arguments. `Pair::new(1, "b")` does not compile, because `T` cannot be
  `i32` and `&str` at once.

You have used generic types since lesson 8: `Vec<T>`, `Option<T>`,
`Result<T, E>` and `HashMap<K, V>` are all written this way. As with
generic functions (lesson 10), the compiler makes a specialised copy for
each type actually used, so generic code costs nothing at run time.

### Bounds on an impl

Inside `impl<T> Pair<T>`, nothing is known about `T`, so `swap` can only move
the values around; it cannot compare or print them. A separate `impl` block
can require abilities, with a bound as in lesson 10:

```rust
impl<T: PartialOrd + Copy> Pair<T> {
    fn larger(&self) -> T {
        if self.first > self.second { self.first } else { self.second }
    }
}
```

`larger` exists only for pairs whose `T` can be compared and copied: a
`Pair<i32>` has it, and a `Pair<Vec<i32>>` does not (a `Vec` is not `Copy`).
Every `Pair` still has `new` and `swap`.

## Lifetimes

Every reference has a **lifetime**: the stretch of the program during which
the value it points at is guaranteed to still exist. Lesson 5's second rule,
"a reference must never outlive the value it points to", is checked with
lifetimes. Inside one function the compiler works them all out itself, which
is why you have not needed to write any so far.

It needs help in one situation: a function that takes references and
**returns** one. Take a function returning the longer of two strings:

```rust
fn longest(a: &str, b: &str) -> &str {
    if a.len() > b.len() { a } else { b }
}
```

```text
error[E0106]: missing lifetime specifier
 --> src/lib.rs:1:33
  |
1 | fn longest(a: &str, b: &str) -> &str {
  |               ----     ----     ^ expected named lifetime parameter
  |
  = help: this function's return type contains a borrowed value, but the signature does not say whether it is borrowed from `a` or `b`
help: consider introducing a named lifetime parameter
  |
1 | fn longest<'a>(a: &'a str, b: &'a str) -> &'a str {
  |           ++++     ++          ++          ++
```

The `help:` states the problem exactly. The result borrows from `a` or from
`b`, depending on the lengths, which are only known at run time. A caller
using the result must know how long it stays valid, which depends on which
input it came from, and the signature does not say. (In lesson 5, `dangle`
got the same error number for a different reason: it had no input to borrow
from at all.)

The fix, as the `help:` suggests, is a **lifetime parameter**. Lifetime names
start with an apostrophe, and are usually short: `'a`, `'b`.

```rust
fn longest<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() > b.len() { a } else { b }
}
```

Piece by piece:

- `<'a>` declares a lifetime parameter, just as `<T>` declares a type
  parameter.
- `a: &'a str` and `b: &'a str` say both inputs are valid for at least the
  span `'a`.
- `-> &'a str` says the result is valid for that same span `'a`.

Together: "the result lives no longer than the **shorter-lived** of the two
inputs", the only promise that is true whichever one is returned.

Lifetime annotations do not change how long anything lives. Nothing is kept
alive longer or dropped earlier. They are a description of a relationship
that the compiler then **checks** at every call. Here the description catches
a real bug:

```rust
fn main() {
    let outer = String::from("a long string");
    let result;
    {
        let inner = String::from("short");
        result = longest(&outer, &inner);
    }                       // inner is dropped here
    println!("{result}");
}
```

```text
error[E0597]: `inner` does not live long enough
  --> src/main.rs:6:34
   |
 5 |         let inner = String::from("short");
   |             ----- binding `inner` declared here
 6 |         result = longest(&outer, &inner);
   |                                  ^^^^^^ borrowed value does not live long enough
 7 |     }
   |     - `inner` dropped here while still borrowed
 8 |     println!("{result}");
   |                ------ borrow later used here
```

As a picture of the spans:

```text
 outer   |--------------------------------------------|
 inner        |-----------|        dropped at the inner }
 'a           |-----------|        no longer than either input
 result used here:                       ^   outside 'a: error
```

Here `result` would actually be `outer`, which is still alive, so this
program would have worked by luck. The compiler does not run the program to
find out; it checks the signature's promise, and the promise only covers
`'a`. Change the strings so `inner` is longer, and the program would really
print freed memory. Move the `println!` inside the block and it compiles.

### Most functions need no annotations

You wrote functions returning references in lesson 5 (`first_word(s: &str)
-> &str`) without any `'a`. That is because of three **lifetime elision**
rules, which fill in the obvious cases:

1. Each reference parameter gets its own lifetime.
2. If there is exactly one reference parameter, the result gets its lifetime:
   the result can only have been borrowed from that one input.
3. In a method, if one of the parameters is `&self` or `&mut self`, the
   result gets `self`'s lifetime.

`longest` has two reference parameters and no `self`, so no rule decides,
and you write it yourself.

## Structs that hold references

A struct can hold a reference instead of owning its data, but then the
struct must not outlive what it borrows from. The struct declares a lifetime
parameter and uses it on the field:

```rust
struct Excerpt<'a> {
    text: &'a str,
}

impl<'a> Excerpt<'a> {
    fn first_word(&self) -> &'a str {
        self.text.split_whitespace().next().unwrap_or("")
    }
}
```

`Excerpt<'a>` reads "an excerpt that borrows from something valid for `'a`".
In `first_word`, the result is `&'a str`, borrowed from the **original
text**, not from the `Excerpt`. Writing `&str` there would have used elision
rule 3 and tied the result to `&self`, the short-lived `Excerpt`. With `'a`,
the word can outlive the `Excerpt` itself, as the program below shows. The
exercise's `first_sentence` has the same signature for the same reason, and
its tests check exactly this.

## 'static

`'static` is the one lifetime with a built-in name: "valid for the whole
run of the program". String literals are `&'static str` because their text
is stored inside the compiled program itself, so it can never be dropped.
That is why earlier lessons could return `"zero"` or `"small"` as
`&'static str` without any input to borrow from.

## Run it

```rust
struct Pair<T> {
    first: T,
    second: T,
}

impl<T> Pair<T> {
    fn new(first: T, second: T) -> Self {
        Self { first, second }
    }
    fn swap(self) -> Self {
        Self { first: self.second, second: self.first }
    }
}

impl<T: PartialOrd + Copy> Pair<T> {
    fn larger(&self) -> T {
        if self.first > self.second { self.first } else { self.second }
    }
}

fn longest<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() > b.len() { a } else { b }
}

struct Excerpt<'a> {
    text: &'a str,
}

impl<'a> Excerpt<'a> {
    fn first_word(&self) -> &'a str {
        self.text.split_whitespace().next().unwrap_or("")
    }
}

fn main() {
    let p = Pair::new(1, 2).swap();
    println!("{} {} {}", p.first, p.second, p.larger());
    println!("{}", Pair::new("a", "b").larger());
    println!("{}", longest("a long string", "short"));

    let text = String::from("call me Ishmael");
    let word;
    {
        let e = Excerpt { text: &text };
        word = e.first_word();
    }   // e is gone, but word borrows from text, not from e
    println!("{word}");
}
```

```output
2 1 2
b
a long string
call
```

After `swap`, the pair is `(2, 1)` and the larger is 2. `&str` is `Copy` and
can be compared, so `Pair<&str>` has `larger` too (`"b"` sorts after `"a"`).

## Your turn

In `src/lib.rs`:

- `longest(a, b)`: the longer string slice. It does not compile as given: add
  the lifetime parameter. When both have the same length, return `a`, the
  first one; the test checks that it is the very same slice (the same place
  in memory), not merely equal text.
- A generic `Stack<T>`, a last-in, first-out pile, stored in its `Vec<T>`:
  - `new()`, an empty stack
  - `push(item)`, put an item on top
  - `pop()`, remove and return the top item, `None` when empty
  - `peek()`, a reference to the top item without removing it, `None` when
    empty
  - `len()` and `is_empty()`
- `Excerpt::first_sentence()`: the text up to and including the first `.`,
  so `"Rust is fast. It is also safe."` gives `"Rust is fast."`; all of the
  text if there is no `.`; and borrowed from the original text, so it stays
  usable after the `Excerpt` is gone
