---
title: Lifetimes in depth
summary: Elision rules, structs and iterators that borrow, several lifetime parameters, and 'static bounds.
order: 10
files: [src/lib.rs]
run: cargo test
hints:
  - "`Tokenizer<'a>` holds `input: &'a str` and a `pos: usize`. `impl<'a> Iterator for Tokenizer<'a> { type Item = &'a str; ... }` so tokens borrow from the input, not from the tokenizer."
  - "In `next`, skip whitespace by advancing `pos` over `self.input[self.pos..].char_indices()`, then find the end of the token the same way, and return `&self.input[start..end]`."
  - "`longest_line(text: &str) -> &str` needs no lifetime: one input reference, so elision ties the result to it. Loop over `text.lines()` and keep a line only if it is strictly longer than the best so far (`max_by_key` would keep the *last* of equal lines)."
  - "`pick_first<'a, 'b>(a: &'a str, _b: &'b str) -> &'a str`: two lifetime parameters say the result is tied only to `a`. `Registry::register(&mut self, name: &'static str)` requires names that live forever, like string literals."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **lifetime annotation** | describes which borrowed input a reference came from; changes nothing at run time |
| **elision rules** | 1: each reference parameter gets a lifetime; 2: one input lifetime goes to every output; 3: `&self`'s lifetime goes to every output |
| **when rule 3 is wrong** | a method returning data borrowed from the input the struct holds, not from the struct |
| **borrows the parser** | an elided return tied to `&self`, so the struct cannot change while it lives |
| **borrowing iterator** | an iterator handing out pieces of borrowed data |
| **`type Item = &'a str`** | items tied to the text, not to the iterator's `&mut self` |
| **several lifetimes** | `'a` and `'b`, so each output says exactly which input it borrows from |
| **signature as promise** | the compiler checks callers against the signature, never against the body |
| **`'static` reference** | can never dangle: literals, constants, leaked memory |
| **`T: 'static` bound** | `T` holds no references that could expire; every owned type meets it |
| **token** | a run of non-whitespace characters |
| **byte index** | a position in a string in bytes; step by whole characters |
| **`as_ptr`** | the address a slice starts at, to check it points into the original |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo check` | shows the starter's lifetime error to fix |
| `cargo test` | compiles and runs the tests |

### Rust names

| Name | What it does |
|---|---|
| `struct Parser<'a> { input: &'a str }` | a struct that borrows |
| `fn rest(&self) -> &str` vs `fn rest2(&self) -> &'a str` | tied to the parser / to the input |
| `struct Tokenizer<'a> { input: &'a str, pos: usize }` | the exercise's iterator |
| `impl<'a> Iterator for Tokenizer<'a> { type Item = &'a str; fn next(&mut self) -> Option<&'a str> }` | a borrowing iterator |
| `s.find(char::is_whitespace)`, `c.is_whitespace()` | the next whitespace; is it whitespace |
| `s.split_at(i)` | cuts a `&str` in two at a byte index |
| `text.lines()` | the lines of a text |
| `fn pick_first<'a, 'b>(a: &'a str, _b: &'b str) -> &'a str` | the result tied only to `a` |
| `fn register(&mut self, name: &'static str)` | accepts only text that lives for the whole run |
| `let mut v = self.names.clone(); v.sort();` | sorts a copy |
| `Box::leak`, `std::thread::spawn` | make a `'static` reference; needs `'static` closures |

### Errors

| Error | Means |
|---|---|
| `error[E0502]: cannot borrow p as mutable because it is also borrowed as immutable` | a result tied to `&self` by rule 3 |
| `error[E0597]: temporary does not live long enough` | a signature that ties the result to an input it does not use |
| `error[E0597]: owned does not live long enough` | borrowed text passed where `&'static str` is required |

---

Beginner lesson 12 introduced lifetime parameters with one example: a
function returning one of two borrowed strings. That covers the idea, but
in real code lifetimes show up in a few more shapes: in structs that borrow,
in iterators over borrowed data, in functions with *several* lifetime
parameters, and as `'static` bounds in library signatures. This lesson goes
through each, with the error you get when it is missing.

A reminder of the one idea underneath all of it: a lifetime annotation does
not change how long anything lives. It **describes** which borrowed input a
reference came from, so the compiler can check, at every call, that the
reference is not used after that input is gone.

## Elision: why you rarely write lifetimes

Every reference in a function signature has a lifetime, but most signatures
do not spell them out. The compiler fills them in with three **elision**
rules:

1. Each reference parameter gets its own lifetime.
2. If there is exactly **one** input lifetime, every output reference gets it.
3. If one parameter is `&self` or `&mut self`, every output reference gets
   **`self`'s** lifetime.

So these need no annotations:

```rust
fn first_word(s: &str) -> &str                   // rule 2: the result borrows from s
impl Doc { fn title(&self) -> &str }             // rule 3: the result borrows from self
```

(Signatures only.) Written out in full, the first is
`fn first_word<'a>(s: &'a str) -> &'a str`: exactly what the compiler
fills in.

You write lifetimes only when the rules cannot decide (two reference inputs
and no `self`, as in Beginner lesson 12's `longest`), or when they decide
**wrongly** for what you mean, which is the next section.

## When rule 3 is wrong

Rule 3 assumes a method returns something borrowed from `self`. For a
struct that itself holds a borrowed reference, that is often not what you
mean:

```rust
struct Parser<'a> {
    input: &'a str,
    pos: usize,
}

impl<'a> Parser<'a> {
    fn rest(&self) -> &str {           // elided: tied to &self, the Parser
        &self.input[self.pos..]
    }
    fn rest2(&self) -> &'a str {       // explicit: tied to 'a, the input text
        &self.input[self.pos..]
    }
    fn advance(&mut self) {
        self.pos += 1;
    }
}
```

The two methods have the same body, and return a slice of the same text.
They differ in what they *promise*, and that decides what the caller may do
afterwards:

```rust
let mut p = Parser { input: "hello", pos: 0 };
let r = p.rest();
p.advance();
println!("{r}");
```

```text
error[E0502]: cannot borrow `p` as mutable because it is also borrowed as immutable
  --> src/main.rs:18:5
   |
17 |     let r = p.rest();
   |             - immutable borrow occurs here
18 |     p.advance();
   |     ^^^^^^^^^^^ mutable borrow occurs here
19 |     println!("{r}");
   |                - immutable borrow later used here
```

With the elided `rest`, `r` counts as a borrow of the **parser**, so the
parser cannot be changed while `r` is alive, even though `r` really points
into `"hello"`, not into the parser. Call `rest2` instead and the same code
compiles: `&'a str` says the slice points into the original input and
lives independently of the parser.

```text
 "hello"      |--------------------------------|  'a: the input text
 Parser p        |-------------------|            the parser, borrowed by &self
 rest():   r is tied to p's borrow
 rest2():  r is tied to 'a, so p can change, or even be dropped
```

Iterators over borrowed data need exactly this, because `next` takes
`&mut self` for every item.

## Iterators that borrow

An iterator that walks borrowed text and hands out pieces of it should give
items borrowed from the **text**, not from the iterator:

```rust
struct Words<'a> {
    rest: &'a str,
}

impl<'a> Iterator for Words<'a> {
    type Item = &'a str;
    fn next(&mut self) -> Option<&'a str> {
        // ...
    }
}
```

(A fragment.) `type Item = &'a str` is the important line. Each call to
`next` borrows the iterator mutably (`&mut self`), only for the length of
that call. If the items were tied to that borrow, you could never hold two
items at once: getting the second one would need a new `&mut` borrow while
the first item still held the old one. Tied to `'a`, the items are
independent of the iterator, so `collect` can gather all of them, and they
stay valid after the iterator is gone:

```rust
let words: Vec<&str> = Words { rest: &text }.collect();   // the iterator is dropped here
println!("{words:?}");                                     // the words are fine
```

The exercise's `Tokenizer` is this pattern, tracking its position as a byte
index `pos` into the input.

## More than one lifetime

A function can have several lifetime parameters, so that each output says
exactly which input it borrows from:

```rust
fn prefix_of<'a, 'b>(haystack: &'a str, needle: &'b str) -> &'a str
```

(A signature.) "The result borrows from `haystack` only; `needle` is only
looked at." With one shared `'a` for both inputs, the signature would claim
the result might borrow from `needle` too, and the compiler would insist
that callers keep `needle` alive as long as they use the result. That is
stricter than necessary, and rejects correct code. The exercise's starter
`pick_first` has that problem:

```rust
fn pick_first<'a>(a: &'a str, _b: &'a str) -> &'a str {
    a
}

fn main() {
    let kept = String::from("kept");
    let result;
    {
        let temporary = String::from("temporary value");
        result = pick_first(&kept, &temporary);
    }
    println!("{result}");
}
```

```text
error[E0597]: `temporary` does not live long enough
  --> src/main.rs:10:36
   |
 9 |         let temporary = String::from("temporary value");
   |             --------- binding `temporary` declared here
10 |         result = pick_first(&kept, &temporary);
   |                                    ^^^^^^^^^^ borrowed value does not live long enough
11 |     }
   |     - `temporary` dropped here while still borrowed
12 |     println!("{result}");
   |                ------ borrow later used here
```

`result` is only ever `kept`, which is still alive, but the signature said
otherwise, and the compiler checks callers against the signature, never
against the body. Giving `_b` its own lifetime `'b`, unrelated to the
result, fixes it. The general lesson: a signature is a promise about the
relationship between inputs and outputs, and a tighter, more accurate promise
lets callers do more.

## 'static

`'static` is the lifetime of things that exist for the whole run of the
program. A **reference** `&'static T` is one that can never dangle: string
literals (their text is inside the compiled program), constants, and memory
deliberately leaked with `Box::leak`.

As a **bound**, `T: 'static` means something different, and the difference
trips people up: "`T` contains no references that could expire", or, put more
plainly, "a value of `T` can be kept as long as you like". Every **owned**
type satisfies it: `String`, `Vec<i32>`, `u32`, a struct of those. It does
**not** mean the value lives forever; a `String` is `'static` in this
sense and is still dropped normally. What fails the bound is a type holding
a borrow of something local, such as `&'a str` for a short `'a`.

That is why `std::thread::spawn` and `Box<dyn Fn() + 'static>` (lesson 8)
ask for `'static`: they will keep the value for an unknown time, so it must
not borrow anything that could be dropped meanwhile.

A function asking for a `&'static str` parameter accepts literals, and
refuses borrowed text that would expire:

```rust
fn main() {
    let mut r = Registry::new();
    r.register("alpha");                   // a literal: &'static str, fine
    let owned = String::from("beta");
    r.register(&owned);                    // error
}
```

```text
error[E0597]: `owned` does not live long enough
  |
8 |     r.register(&owned);
  |     -----------^^^^^^-
  |     |          |
  |     |          borrowed value does not live long enough
  |     argument requires that `owned` is borrowed for `'static`
9 | }
  | - `owned` dropped here while still borrowed
```

## Run it

```rust
struct Words<'a> {
    rest: &'a str,
}

impl<'a> Iterator for Words<'a> {
    type Item = &'a str;
    fn next(&mut self) -> Option<&'a str> {
        let trimmed = self.rest.trim_start();
        if trimmed.is_empty() {
            return None;
        }
        let end = trimmed.find(' ').unwrap_or(trimmed.len());
        let (word, rest) = trimmed.split_at(end);
        self.rest = rest;
        Some(word)
    }
}

fn prefix_of<'a, 'b>(haystack: &'a str, needle: &'b str) -> &'a str {
    match haystack.find(needle) {
        Some(i) => &haystack[..i],
        None => haystack,
    }
}

fn main() {
    let text = String::from("the quick  brown fox");
    let words: Vec<&str> = Words { rest: &text }.collect();   // the iterator is gone...
    println!("{words:?}");                                     // ...the words remain

    let before;
    {
        let needle = String::from("brown");
        before = prefix_of(&text, &needle);
    }   // needle is dropped; before borrows only from text
    println!("[{before}]");
}
```

```output
["the", "quick", "brown", "fox"]
[the quick  ]
```

`Words::next` keeps a shrinking slice `rest` instead of a position: each
call skips leading spaces, splits off the word, and keeps what is after it.
`split_at(end)` cuts a `&str` into two at a byte index, both halves still
borrowing from `text`. `prefix_of` returned the text before `"brown"`,
including its two spaces, and it stayed usable after `needle` was dropped
because its signature ties it only to `haystack`.

## Your turn

In `src/lib.rs`:

- `Tokenizer<'a>`: an `Iterator` over the tokens of its input, a token being
  a run of non-whitespace characters. Any whitespace separates tokens:
  spaces, tabs and newlines, so `"  let x =\t42 ;\n"` gives `"let"`, `"x"`,
  `"="`, `"42"`, `";"`. Items are `&'a str`, slices of the input:
  - the tests collect the tokens inside a block, drop the tokenizer, and use
    them afterwards, so they must not borrow from the tokenizer
  - they check that the first token points at the start of the input
    (`as_ptr`), so return slices, not new `String`s
  - the input may contain multi-byte characters (`"héllo wörld"`); use
    `char_indices` or `char::is_whitespace` with `find`, and never step `pos`
    by 1 byte blindly
  - input that is only whitespace yields nothing
- `longest_line(text)`: the longest line, by `.len()`, borrowed from `text`;
  on a tie the **first** one (`"a\nbbb\ncc\nddd"` gives `"bbb"`); `""` for
  empty text
- `pick_first(a, b)`: returns `a`. Change the starter's signature so the
  result is tied only to `a`'s lifetime; the body stays the same.
- `Registry`: stores `&'static str` names.
  - `register(&mut self, name: &'static str)`
  - `names(&self) -> Vec<&'static str>`: all names, sorted alphabetically
    (sort a copy, leaving the stored order alone)
