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

## Generics

Generic code is written once, with a type parameter standing in for the real
type:

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

You have used generics since the first Rust lesson: `Vec<T>`, `Option<T>`,
`Result<T, E>` and `HashMap<K, V>` are all generic.

An `impl` block can require abilities from `T`:

```rust
impl<T: PartialOrd + Copy> Pair<T> {
    fn larger(&self) -> T {
        if self.first > self.second { self.first } else { self.second }
    }
}
```

`larger` only exists for pairs whose `T` can be compared and copied.

## Lifetimes

Every reference has a **lifetime**: the stretch of code where the value it
points at is still valid. Usually the compiler works these out itself. It
needs help when a function returns a reference and it cannot tell which input
that reference comes from:

```rust
fn longest(a: &str, b: &str) -> &str {   // error: missing lifetime specifier
    if a.len() > b.len() { a } else { b }
}
```

The fix is a lifetime parameter, conventionally `'a`:

```rust
fn longest<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() > b.len() { a } else { b }
}
```

Read it as: "the result lives no longer than **both** inputs". Lifetime
annotations do not change how long anything lives. They describe a
relationship so the compiler can check callers:

```rust
let outer = String::from("a long string");
let result;
{
    let inner = String::from("short");
    result = longest(&outer, &inner);
}                       // inner is dropped here
println!("{result}");   // error: `inner` does not live long enough
```

## Structs that hold references

A struct that borrows data needs a lifetime too, so it cannot outlive what it
points at:

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

The returned `&'a str` borrows from the original text, not from the
`Excerpt`, so it can outlive the struct itself.

## 'static

`'static` means "valid for the whole program". String literals are
`&'static str` because they are baked into the binary, which is why functions
returning literals could use `&'static str` in earlier lessons.

## Your turn

In `src/lib.rs`:

- `longest(a, b)`: the longer string slice (the first one if they are equal)
- A generic `Stack<T>` with `new`, `push`, `pop` (an `Option<T>`),
  `peek` (an `Option<&T>`), `len` and `is_empty`
- `Excerpt::first_sentence()`: the text up to and including the first `.`,
  or all of it if there is no `.`, borrowed from the original text
