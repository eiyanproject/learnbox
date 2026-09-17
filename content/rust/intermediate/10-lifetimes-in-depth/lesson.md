---
title: Lifetimes in depth
summary: Elision rules, structs and iterators that borrow, several lifetime parameters, and 'static bounds.
order: 10
files: [src/lib.rs]
run: cargo test
hints:
  - "`Tokenizer<'a>` holds `input: &'a str` and a `pos: usize`. `impl<'a> Iterator for Tokenizer<'a> { type Item = &'a str; ... }` so tokens borrow from the input, not from the tokenizer."
  - "In `next`, skip whitespace by advancing `pos` over `self.input[self.pos..].char_indices()`, then find the end of the token the same way, and return `&self.input[start..end]`."
  - "`longest_line<'a>(text: &'a str) -> &'a str`: `text.lines().max_by_key(|l| l.len()).unwrap_or(\"\")`. With one input reference, elision would allow leaving `'a` out entirely."
  - "`pick_first<'a, 'b>(a: &'a str, _b: &'b str) -> &'a str`: two lifetime parameters say the result is tied only to `a`. `Registry::register(&mut self, name: &'static str)` requires names that live forever, like string literals."
---

The Beginner lesson introduced `'a` for a function returning one of two
borrowed inputs. This lesson covers the rest of what you meet in practice.

## Elision: why you rarely write lifetimes

The compiler fills in lifetimes on function signatures by three rules:

1. Each reference parameter gets its own lifetime.
2. If there is exactly **one** input lifetime, outputs get it.
3. If there is `&self` or `&mut self`, outputs get **its** lifetime.

So these need no annotations:

```rust
fn first_word(s: &str) -> &str                   // rule 2
impl Doc { fn title(&self) -> &str }             // rule 3
```

You only write lifetimes when the rules are ambiguous (two inputs, no `self`),
or when rule 3 picks the wrong one.

## When rule 3 is wrong

```rust
struct Parser<'a> {
    input: &'a str,
}

impl<'a> Parser<'a> {
    fn rest(&self) -> &str { ... }       // elided: borrows from &self
    fn rest2(&self) -> &'a str { ... }   // explicit: borrows from the input
}
```

With the elided version, the returned slice keeps the **parser** borrowed, so
you cannot use the parser mutably again while holding it. Returning `&'a str`
says the slice points into the original input and lives independently of the
parser. Iterators over borrowed data need exactly this.

## Iterators that borrow

```rust
struct Words<'a> {
    rest: &'a str,
}

impl<'a> Iterator for Words<'a> {
    type Item = &'a str;
    fn next(&mut self) -> Option<&'a str> { ... }
}
```

Now `let words: Vec<&str> = Words { rest: &text }.collect();` works: the
iterator is gone but the words, borrowed from `text`, remain.

## More than one lifetime

```rust
fn prefix_of<'a, 'b>(haystack: &'a str, needle: &'b str) -> &'a str
```

This says the result borrows only from `haystack`. With a single shared `'a`
the caller would have to keep `needle` alive for as long as the result, which is
stricter than necessary.

## 'static

`&'static T` lives for the whole program (string literals, leaked allocations).
As a **bound**, `T: 'static` means "`T` contains no non-static borrows", which
is what `thread::spawn` and `Box<dyn Trait + 'static>` require: owned data like
`String` satisfies it. It does **not** mean the value lives forever.

## Your turn

In `src/lib.rs`:

- `Tokenizer<'a>`: an iterator over whitespace-separated tokens of an input
  `&'a str`, yielding `&'a str` slices of the input
- `longest_line(text)`: the longest line (the first one on ties), borrowed
- `pick_first(a, b)`: returns `a`, with a signature that ties the result only to `a`
- `Registry`: stores `&'static str` names; `register(name)`, `names()` sorted
