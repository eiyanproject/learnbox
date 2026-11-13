---
title: Borrowing and slices
summary: Use a value without taking it; one writer or many readers; views into strings and arrays.
order: 5
files: [src/lib.rs]
run: cargo test
hints:
  - "`first_word`: loop over `s.char_indices()`; at the first `' '` return `&s[..i]`. If there is no space, return `s` itself."
  - "`sum` takes `&[i32]`. `for n in nums { total += n; }` works because adding a `&i32` to an `i32` is allowed, or write `*n`."
  - "`double_all` takes `&mut [i32]`: `for n in nums.iter_mut() { *n *= 2; }`. The `*` writes through the reference."
  - "`append_greeting(buf: &mut String, name: &str)`: `buf.push_str(\"Hello, \"); buf.push_str(name); buf.push('\\n');`"
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **borrow** | use a value through a reference without owning it |
| **reference** | a pointer to a value that does not own it: `&T` |
| **shared reference** (`&T`) | read-only; any number may exist at once |
| **mutable reference** (`&mut T`) | can change the value; only one at a time, and no shared ones meanwhile |
| **the borrowing rule** | either any number of `&T` or exactly one `&mut T`, never both |
| **dangling reference** | one pointing at memory that has been freed; Rust refuses to compile it |
| **reallocate** | a full vector moving its items to a new, bigger block |
| **last use** | a borrow lasts until the reference is last used, not to the end of the block |
| **non-lexical lifetimes** | that rule: a borrow's length follows how the reference is used |
| **lifetime** | how long a reference is valid (Learn lesson 12) |
| **dereference** (`*`) | follow a reference to the value behind it |
| **auto-dereference** | method calls and most operators follow references for you |
| **slice** | a reference to a contiguous part of a string, array or vector, without copying |
| **string slice** (`&str`) | a slice of text; functions should take `&str`, not `&String` |
| **`&[T]`** | a slice of a vector or array; take it rather than `&Vec<T>` |
| **byte position** | string slices are cut at bytes; cutting inside a multi-byte character panics |
| **in place** | changing the given values themselves rather than returning new ones |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo check`, `cargo test` | check the borrows; run the tests |

### Rust names

| Name | What it does |
|---|---|
| `&name`, `fn len(s: &String)` | borrow; a parameter that borrows |
| `&mut msg`, `fn add(s: &mut String)` | lend mutably; a parameter that may change it |
| `*n += 1` | writes through a mutable reference |
| `&s[0..5]`, `&s[6..]`, `&v[1..3]` | slices: up to but not including the end |
| `s.find(' ')` | the byte position of the first space, or `None` |
| `s.char_indices()` | each character with its byte position |
| `s.len()`, `s.chars().count()` | length in bytes; in characters |
| `for n in nums.iter_mut()` | each item as a `&mut`, to change it |
| `buf.push_str("...")` | adds text to the end of a `String` |

### Errors

| Error | Means |
|---|---|
| `error[E0502]: cannot borrow v as mutable because it is also borrowed as immutable` | a shared and a mutable borrow overlap |
| `error[E0106]: missing lifetime specifier` | a returned reference with nothing to borrow from |
| `cannot borrow *s as mutable, as it is behind a & reference` | writing through a read-only reference |
| `byte index 3 is not a char boundary` | a panic from slicing inside a multi-byte character |

---

Moving a value into every function that wants to look at it would be
tiresome: the function would have to hand it back every time, or the caller
would lose it. Instead, you **borrow** it with a reference. It works like
lending someone a book: they can read it (or, if you allow it, write in
it), but it is still yours, and they must give it back before you can throw
it away.

## References

```rust
fn length(s: &String) -> usize {
    s.len()
}

let name = String::from("Ana");
let n = length(&name);    // lend it
println!("{name}");       // still ours
```

(A fragment.) `&name` creates a **reference**: a pointer to `name` that does
not own it. The parameter type `&String` says "a reference to a `String`".
The function gets to use the value but not own it, and when the function
returns, nothing is dropped, because the reference never owned anything.
Creating a reference is called **borrowing**.

## Mutable references

To let a function change a value, lend it mutably:

```rust
fn add_bang(s: &mut String) {
    s.push('!');
}

let mut msg = String::from("hi");
add_bang(&mut msg);       // msg is now "hi!"
```

Three things have to agree: the variable is `mut`, the call passes
`&mut msg`, and the parameter type is `&mut String`. A plain `&` reference is
read-only, so `s.push` through one fails to compile.

## The borrowing rule

At any moment you can have **either**:

- any number of shared references `&T`, **or**
- exactly one mutable reference `&mut T`

but not both. This is checked at compile time and rules out a whole class of
bugs, such as changing a vector while something else is reading it:

```rust
let mut v = vec![1, 2, 3];
let first = &v[0];
v.push(4);                // error: cannot borrow `v` as mutable
println!("{first}");      // because `first` is still in use here
```

The compiler explains exactly which borrows collide, and where:

```text
error[E0502]: cannot borrow `v` as mutable because it is also borrowed as immutable
  |
3 |     let first = &v[0];
  |                  - immutable borrow occurs here
4 |     v.push(4);
  |     ^^^^^^^^^ mutable borrow occurs here
5 |     println!("{first}");
  |                ----- immutable borrow later used here
```

Read the three labels top to bottom: a shared borrow starts on line 3, a
mutable borrow happens on line 4, and the shared one is still needed on line
5, so the two overlap.

Why is that dangerous? A vector keeps its items in one block of heap
memory. When it is full, `push` moves everything to a new, bigger block and
frees the old one. `first` points into the old block, so after the push it
would point at freed memory, a **dangling reference**. In C or C++ this
compiles, and reads garbage or crashes at some later moment. The compiler
refuses.

A borrow lasts until its **last use**, not until the end of the block. Move
the `println!` above the `push` and the code compiles: `first` is no longer
used after that line, so its borrow has ended before `push` starts. This is
called **non-lexical lifetimes**: the borrow's length follows how the
reference is used, not the block it sits in.

## References must always be valid

Let's try to make a reference outlive the value it points to:

```rust
fn dangle() -> &String {
    let s = String::from("hello");
    &s              // s is dropped when the function ends...
}                   // ...so this reference would point at nothing
```

```text
error[E0106]: missing lifetime specifier
  |
1 | fn dangle() -> &String {
  |                ^ expected named lifetime parameter
  |
  = help: this function's return type contains a borrowed value, but there is no value for it to be borrowed from
```

The message mentions lifetimes, which are lesson 12. Ignore that part for
now; the `help:` line holds the key: there is no value for the reference to
borrow from. The fix is to return the `String` itself, moving ownership out
to the caller, which the compiler also suggests further down.

To recap, the two rules of references:

1. At any moment, **either** any number of shared references **or** one
   mutable reference.
2. A reference must never outlive the value it points to.

## Dereferencing

`*` follows a reference to the value behind it:

```rust
let mut x = 5;
let r = &mut x;
*r += 1;                  // x is now 6
```

Method calls and most operators dereference automatically, which is why you
rarely see `*` except when writing through `&mut`.

## Slices

A **slice** is a reference to part of a sequence: a contiguous run of a
string, array or vector, without copying it. `[start..end]` picks positions
`start` up to but not including `end`; leave out either end to go to the
edge.

```rust
let s = String::from("hello world");
let hello: &str = &s[0..5];
let world: &str = &s[6..];

let nums = [10, 20, 30, 40];
let middle: &[i32] = &nums[1..3];    // [20, 30]
```

`&str` is a string slice. That is why functions should take `&str` rather than
`&String`: a `&String`, a string literal and a slice of either all work.
Likewise, take `&[T]` rather than `&Vec<T>`.

String slice positions are **bytes**. Slicing in the middle of a multi-byte
character panics, so find positions with `char_indices()` or `find()` rather
than guessing.

## Run it

```rust
fn length(s: &String) -> usize {
    s.len()
}

fn add_bang(s: &mut String) {
    s.push('!');
}

fn main() {
    let name = String::from("Ana");
    let n = length(&name);
    println!("{name} {n}");

    let mut msg = String::from("hi");
    add_bang(&mut msg);
    println!("{msg}");

    let mut x = 5;
    let r = &mut x;
    *r += 1;
    println!("{x}");

    let s = String::from("hello world");
    println!("[{}] [{}]", &s[0..5], &s[6..]);
    let nums = [10, 20, 30, 40];
    println!("{:?}", &nums[1..3]);

    let word = "naïve";
    println!("{} bytes, {} chars, ï at byte {:?}", word.len(), word.chars().count(), word.find('ï'));
}
```

```output
Ana 3
hi!
6
[hello] [world]
[20, 30]
6 bytes, 5 chars, ï at byte Some(2)
```

`ï` takes two bytes, so `&word[0..3]` would end in the middle of it and panic.

## Your turn

In `src/lib.rs`:

- `first_word(s)`: the text up to the first space, as a slice of `s` (no new
  `String`): `first_word("hello world")` is `"hello"`. No space means the
  whole string.
- `sum(nums)`: the sum of a slice of `i32`, `0` for an empty slice
- `double_all(nums)`: double every number **in place**, through the mutable
  slice it is given; it returns nothing
- `append_greeting(buf, name)`: add the line `Hello, <name>` and a newline to
  the end of `buf`, keeping what `buf` already holds
